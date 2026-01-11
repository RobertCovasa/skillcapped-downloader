import asyncio
import os
import shutil
import re
import sys
from pathlib import Path
from typing import List, Tuple

import aiohttp
import m3u8
from tqdm.asyncio import tqdm

# --- CONFIGURATION ---
CONCURRENT_DOWNLOADS = 10
FFMPEG_CHECK = True  # Set False if you do not have FFmpeg installed

class SkillCappedDownloader:
    def __init__(self):
        self.api_template = "https://www.skill-capped.com/api/video/{}/4500.m3u8"

    def sanitize_filename(self, name: str) -> str:
        """Removes characters that are illegal in Windows filenames."""
        # Remove invalid chars: < > : " / \ | ? *
        clean = re.sub(r'[<>:"/\\|?*]', '', name)
        # Strip trailing spaces or dots (Windows doesn't like file names ending in .)
        return clean.strip().rstrip('.')

    async def probe_video_id(self, session, url_segment):
        """Checks if a URL segment is a valid Video ID by hitting the API."""
        manifest_url = self.api_template.format(url_segment)
        try:
            async with session.head(manifest_url) as resp:
                return manifest_url if resp.status == 200 else None
        except:
            return None

    async def find_valid_manifest(self, url: str):
        """
        Smart Probe: Splits the URL and checks the last few segments 
        to see which one acts as the valid Video ID.
        """
        parts = [p for p in url.split('/') if p and '.' not in p]
        
        # Check last 3 segments in reverse order
        candidates = parts[-3:] 
        candidates.reverse()

        print(f"[*] Probing URL: {url}")
        
        async with aiohttp.ClientSession() as session:
            for candidate in candidates:
                valid_url = await self.probe_video_id(session, candidate)
                if valid_url:
                    return candidate, valid_url
        
        return None, None

    async def download_video(self, video_id: str, file_name: str, output_folder: Path, manifest_url: str):
        final_mp4_path = output_folder / f"{file_name}.mp4"
        temp_dir = output_folder / f"temp_{video_id}"

        if final_mp4_path.exists():
            print(f"[+] Skipping '{file_name}' (already exists).")
            return

        print(f"[*] Processing: {file_name}")

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
        
        semaphore = asyncio.Semaphore(CONCURRENT_DOWNLOADS)
        
        print(f"    - Downloading {len(playlist.segments)} segments...")

        async with aiohttp.ClientSession() as session:
            tasks = []
            for i, segment in enumerate(playlist.segments):
                seg_name = f"seg_{i:05d}.ts"
                seg_path = temp_dir / seg_name
                segment_files.append(seg_path)
                
                # Resumable check
                if seg_path.exists() and seg_path.stat().st_size > 0:
                    continue

                tasks.append(self.fetch_segment(session, semaphore, segment.absolute_uri, seg_path))

            if tasks:
                for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), unit="seg", desc="    Progress"):
                    await f

        # 4. Mux to MP4
        await self.merge_segments(segment_files, final_mp4_path, temp_dir)

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

    async def merge_segments(self, segment_files: List[Path], output_path: Path, temp_dir: Path):
        print(f"    - Merging into {output_path.name}...")
        
        list_file_path = temp_dir / "files.txt"
        with open(list_file_path, 'w') as f:
            for seg in segment_files:
                clean_path = str(seg.absolute()).replace('\\', '/')
                f.write(f"file '{clean_path}'\n")

        if FFMPEG_CHECK:
            try:
                cmd = [
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(list_file_path), "-c", "copy", str(output_path)
                ]
                process = await asyncio.create_subprocess_exec(
                    *cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
                )
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

async def main():
    if not os.path.exists("inputs.txt"):
        print("Error: inputs.txt not found. Please create it with format: Course Name, Video Name, URL")
        return

    with open("inputs.txt", "r") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]

    downloader = SkillCappedDownloader()

    for line in lines:
        parts = line.split(",")
        
        # VALIDATION: We now expect 3 parts (Course, Video Name, URL)
        if len(parts) < 3:
            print(f"[!] Skipped invalid line (needs 3 parts): {line}")
            continue
        
        raw_course_name = parts[0].strip()
        raw_video_name = parts[1].strip()
        url = parts[2].strip()

        # Sanitize Names for Windows
        course_name = downloader.sanitize_filename(raw_course_name)
        video_name = downloader.sanitize_filename(raw_video_name)

        # Create Course Folder
        output_dir = Path(course_name)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Find ID and Download
        video_id, manifest_url = await downloader.find_valid_manifest(url)

        if video_id:
            await downloader.download_video(video_id, video_name, output_dir, manifest_url)
        else:
            print(f"[!] Could not find video ID for: {url}")

    print("\nAll downloads completed.")

if __name__ == "__main__":
    asyncio.run(main())