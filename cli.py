import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

# Local modules
from downloader import SkillCappedDownloader
from scraper import scrape_details
from utils import sanitize_filename, parse_title_metadata

async def main():
    if not os.path.exists("inputs.txt"):
        print("Error: inputs.txt not found.")
        return

    with open("inputs.txt", "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith("#")]

    if not lines:
        print("[!] No tasks found.")
        return

    downloader = SkillCappedDownloader()
    
    # Initialize Playwright if needed
    playwright = None
    browser = None
    page = None
    needs_scraping = any(len(line.split(",")) < 3 for line in lines)

    if needs_scraping:
        print("[*] Launching browser for auto-detection...")
        playwright = await async_playwright().start()
        browser = await playwright.firefox.launch(headless=True)
        page = await browser.new_page()

    try:
        for line in lines:
            parts = line.split(",")
            
            # --- Magic Mode (URL Only) ---
            if len(parts) < 3:
                url = parts[0].strip()
                if not url.startswith("http"): continue
                
                raw_course, raw_video = await scrape_details(page, url)
                if not raw_course:
                    print(f"[!] Could not auto-detect names for {url}. Skipping.")
                    continue
            # --- Manual Mode ---
            else:
                raw_course = parts[0].strip()
                raw_video = parts[1].strip()
                url = parts[2].strip()

            # Process
            course_name = sanitize_filename(raw_course)
            video_name = sanitize_filename(raw_video)
            meta_title, meta_track = parse_title_metadata(raw_video)
            
            metadata = {
                "album": raw_course,
                "title": meta_title,
                "track": meta_track
            }

            output_dir = Path(course_name)
            output_dir.mkdir(parents=True, exist_ok=True)

            video_id, manifest_url, _ = await downloader.find_valid_manifest(url)

            if video_id:
                await downloader.download_video(video_id, video_name, output_dir, manifest_url, metadata)
            else:
                print(f"[!] Could not find video ID for: {url}")

    finally:
        if browser: await browser.close()
        if playwright: await playwright.stop()

    print("\nAll downloads completed.")

if __name__ == "__main__":
    asyncio.run(main())