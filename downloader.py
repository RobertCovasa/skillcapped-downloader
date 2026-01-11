import asyncio
import shutil
import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict

import aiohttp
import m3u8
from tqdm.asyncio import tqdm

# Import local modules
import config
from utils import sanitize_filename, parse_title_metadata

class SkillCappedDownloader:
    def __init__(self, quality_priority: List[str] = None):
        self.api_template = "https://www.skill-capped.com/api/video/{}/{}.m3u8"
        self.quality_priority = quality_priority if quality_priority else config.DEFAULT_PRIORITY

    async def check_quality_url(self, session, video_id, quality):
        url = self.api_template.format(video_id, quality)
        try:
            async with session.head(url) as resp:
                return url if resp.status == 200 else None
        except:
            return None

    async def find_valid_manifest(self, url: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        parts = [p for p in url.split('/') if p and '.' not in p]
        candidates = parts[-3:] 
        candidates.reverse()

        print(f"[*] Probing URL for ID: {url}")
        
        async with aiohttp.ClientSession() as session:
            for video_id in candidates:
                for q in self.quality_priority:
                    valid_url = await self.check_quality_url(session, video_id, q)
                    if valid_url:
                        print(f"    -> Found ID: {video_id} | Quality: {q}")
                        return video_id, valid_url, q
        
        return None, None, None

    async def download_video(self, video_id: str, file_name: str, output_folder: Path, manifest_url: str, metadata: Dict):
        final_mp4_path = output_folder / f"{file_name}.mp4"
        temp_dir = output_folder / f"temp_{video_id}"

        if final_mp4_path.exists():
            print(f"[+] Skipping '{file_name}' (already exists).")
            return

        print(f"[*] Downloading: {file_name}")

        # 1. Fetch Manifest
        async with aiohttp.ClientSession() as session:
            async with session.get(manifest_url) as resp:
                if resp.status != 200:
                    print(f"[!] Failed to fetch manifest. Status: {resp.status}")
                    return
                m3u8_content = await resp.text()

        # 2. Parse Manifest
        playlist = m3u8.loads(m3u8_content, uri=manifest_url)
        if not playlist.segments:
            print("[!] No segments found.")
            return

        # 3. Download Segments
        temp_dir.mkdir(parents=True, exist_ok=True)
        segment_files = []
        semaphore = asyncio.Semaphore(config.CONCURRENT_DOWNLOADS)
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i, segment in enumerate(playlist.segments):
                seg_name = f"seg_{i:05d}.ts"
                seg_path = temp_dir / seg_name
                segment_files.append(seg_path)
                
                if seg_path.exists() and seg_path.stat().st_size > 0:
                    continue

                tasks.append(self.fetch_segment(session, semaphore, segment.absolute_uri, seg_path))

            if tasks:
                for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), unit="seg", desc="    Progress"):
                    await f

        # 4. Mux to MP4
        await self.merge_segments(segment_files, final_mp4_path, temp_dir, metadata)

    async def fetch_segment(self, session, semaphore, url, path):
        async with semaphore:
            retries = 3
            while retries > 0:
                try:
                    async with session.get(url) as resp:
                        resp.raise_for_status()
                        data = await resp.read()
                        with open(path, 'wb') as f:
                            f.write(data)
                        return
                except Exception:
                    retries -= 1
                    await asyncio.sleep(1)

    async def merge_segments(self, segment_files: List[Path], output_path: Path, temp_dir: Path, metadata: Dict):
        print(f"    - Merging into {output_path.name}...")
        
        list_file_path = temp_dir / "files.txt"
        with open(list_file_path, 'w') as f:
            for seg in segment_files:
                clean_path = str(seg.absolute()).replace('\\', '/')
                f.write(f"file '{clean_path}'\n")

        if config.FFMPEG_CHECK:
            try:
                cmd = [
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(list_file_path),
                    "-c", "copy",
                    "-metadata", f"title={metadata.get('title', '')}",
                    "-metadata", f"album={metadata.get('album', '')}",
                    "-metadata", "artist=SkillCapped",
                    "-loglevel", "error" 
                ]
                if metadata.get('track'):
                    cmd.extend(["-metadata", f"track={metadata['track']}"])

                cmd.append(str(output_path))

                process = await asyncio.create_subprocess_exec(*cmd)
                await process.wait()
                
                if process.returncode == 0:
                    shutil.rmtree(temp_dir)
                    print(f"    [+] Finished: {output_path.name}")
                else:
                    print("[!] FFmpeg Error.")
            except FileNotFoundError:
                print("[!] FFmpeg not found.")
        else:
            with open(output_path.with_suffix('.ts'), 'wb') as merged:
                for seg in segment_files:
                    with open(seg, 'rb') as f:
                        merged.write(f.read())
            shutil.rmtree(temp_dir)