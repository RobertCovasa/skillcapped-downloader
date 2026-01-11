import asyncio
import os
import shutil
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict

import aiohttp
import m3u8
from tqdm.asyncio import tqdm
from playwright.async_api import async_playwright

# --- CONFIGURATION ---
CONCURRENT_DOWNLOADS = 10
FFMPEG_CHECK = True

# Quality Priority List: The script tries these in order.
# 4500 = 1080p @ 60fps (Best)
# 2500 = 1080p @ 60fps (Standard)
# 1500 = 720p  @ 30fps (Medium)
# 500  = 480p  @ 30fps (Low)
QUALITY_PRIORITY = ["4500", "2500", "1500", "500"]

class SkillCappedDownloader:
    def __init__(self):
        self.api_template = "https://www.skill-capped.com/api/video/{}/{}.m3u8"

    def sanitize_filename(self, name: str) -> str:
        """Removes characters that are illegal in Windows filenames."""
        clean = re.sub(r'[<>:"/\\|?*]', '', name)
        return clean.strip().rstrip('.')

    def parse_title_metadata(self, video_name: str) -> Tuple[str, Optional[str]]:
        """Extracts track number and clean title from strings like '01 - Intro'."""
        match = re.match(r'^(\d+)[ .-]+(.*)', video_name)
        if match:
            track_num = match.group(1)
            clean_title = match.group(2).strip()
            return clean_title, track_num
        return video_name, None

    async def check_quality_url(self, session, video_id, quality):
        url = self.api_template.format(video_id, quality)
        try:
            async with session.head(url) as resp:
                return url if resp.status == 200 else None
        except:
            return None

    async def find_valid_manifest(self, url: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        # Extract potential IDs from the URL (last 3 parts)
        parts = [p for p in url.split('/') if p and '.' not in p]
        candidates = parts[-3:] 
        candidates.reverse()

        print(f"[*] Probing URL for ID: {url}")
        
        async with aiohttp.ClientSession() as session:
            for video_id in candidates:
                for q in QUALITY_PRIORITY:
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
        semaphore = asyncio.Semaphore(CONCURRENT_DOWNLOADS)
        
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

        if FFMPEG_CHECK:
            try:
                cmd = [
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(list_file_path),
                    "-c", "copy",
                    "-metadata", f"title={metadata.get('title', '')}",
                    "-metadata", f"album={metadata.get('album', '')}",
                    "-metadata", "artist=SkillCapped",
                    # Suppress output unless error
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
            # Simple concatenation fallback
            with open(output_path.with_suffix('.ts'), 'wb') as merged:
                for seg in segment_files:
                    with open(seg, 'rb') as f:
                        merged.write(f.read())
            shutil.rmtree(temp_dir)

# --- SCRAPER HELPER ---
async def scrape_details(page, url):
    """Uses Playwright page to extract Course Name and Video Title."""
    print(f"[*] Scraping details for: {url}")
    try:
        # Fast load strategy: 'domcontentloaded' ignores heavy assets (video/images)
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # Wait for the Course Title element (Proof that JS loaded)
        try:
            await page.wait_for_selector(".css-1rwlwny", state="visible", timeout=10000)
        except:
            print(f"    [!] Timeout waiting for page content. Skipping auto-detect.")
            return None, None

        # 1. Course Name
        course_el = await page.query_selector(".css-1rwlwny")
        raw_course = await course_el.inner_text() if course_el else "Unknown Course"
        course_name = " ".join(raw_course.split()).title() # Clean & Title Case

        # 2. Video Title (Split across multiple divs)
        parts = await page.query_selector_all(".css-1juj8ih")
        title_words = []
        for part in parts:
            text = await part.inner_text()
            if text.strip():
                title_words.append(text.strip())
        
        video_title = " ".join(title_words).title() if title_words else "Unknown Video"

        print(f"    [+] Detected: {course_name} | {video_title}")
        return course_name, video_title

    except Exception as e:
        print(f"    [!] Scraper Error: {e}")
        return None, None

async def main():
    if not os.path.exists("inputs.txt"):
        print("Error: inputs.txt not found.")
        return

    with open("inputs.txt", "r") as f:
        # Filter comments and empty lines
        lines = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith("#")]

    if not lines:
        print("[!] No tasks found.")
        return

    downloader = SkillCappedDownloader()
    
    # Initialize Playwright (Browser) only if needed
    playwright = None
    browser = None
    page = None

    # Check if we have any URL-only lines that need scraping
    needs_scraping = any(len(line.split(",")) < 3 for line in lines)

    if needs_scraping:
        print("[*] Launching browser for auto-detection...")
        playwright = await async_playwright().start()
        # Headless=True is faster. If it hangs, set to False.
        browser = await playwright.firefox.launch(headless=True)
        page = await browser.new_page()

    try:
        for line in lines:
            parts = line.split(",")
            
            # --- CASE 1: Full Manual Input (Legacy) ---
            if len(parts) >= 3:
                raw_course = parts[0].strip()
                raw_video = parts[1].strip()
                url = parts[2].strip()
            
            # --- CASE 2: URL Only (Auto-Magic) ---
            else:
                url = parts[0].strip()
                if not url.startswith("http"):
                    print(f"[!] Invalid line skipped: {line}")
                    continue
                
                # Use the browser to find names
                raw_course, raw_video = await scrape_details(page, url)
                
                if not raw_course or not raw_video:
                    print(f"[!] Could not auto-detect names for {url}. Skipping.")
                    continue

            # Standard Processing
            course_name = downloader.sanitize_filename(raw_course)
            video_name = downloader.sanitize_filename(raw_video)
            
            # Extract clean metadata
            meta_title, meta_track = downloader.parse_title_metadata(raw_video)
            metadata = {
                "album": raw_course,
                "title": meta_title,
                "track": meta_track
            }

            output_dir = Path(course_name)
            output_dir.mkdir(parents=True, exist_ok=True)

            video_id, manifest_url, quality = await downloader.find_valid_manifest(url)

            if video_id:
                await downloader.download_video(video_id, video_name, output_dir, manifest_url, metadata)
            else:
                print(f"[!] Could not find video ID for: {url}")

    finally:
        # Clean up browser
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()

    print("\nAll downloads completed.")

if __name__ == "__main__":
    asyncio.run(main())