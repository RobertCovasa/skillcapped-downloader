# SkillCapped Downloader

A fast, async downloader for Skill-Capped. Automatically organizes videos into folders and muxes them into clean MP4s using FFmpeg.

## ⚡ Features
* **Fast & Resumable:** Concurrent downloads via `aiohttp`; restarts exactly where it left off.
* **Adaptive Quality:** Automatically prioritizes **1080p @ 60fps (High Bitrate)**. If unavailable, it falls back to Standard 1080p (60fps), 720p (30fps), or 480p (30fps).
* **High Quality Output:** Lossless `.ts` to `.mp4` muxing (no re-encoding).
* **Smart Parsing:** Auto-detects video IDs from standard URLs.

## 🛠️ Setup
1.  **Install Python 3.8+**
2.  **Install FFmpeg:** Ensure `ffmpeg` is accessible in your system PATH.
3.  **Install Dependencies:**
    ```bash
    git clone [https://github.com/yourusername/skillcapped-downloader.git](https://github.com/yourusername/skillcapped-downloader.git)
    cd skillcapped-downloader
    pip install -r requirements.txt
    ```

## 🚀 Usage
1.  **Configure `inputs.txt`:**
    Add lines in the format: `Course Name, Video Title, URL`
    ```csv
    Jungle Guide, 01 - Intro, LINK
    
    # Comments are supported
    ```

2.  **Run the script:**
    ```bash
    python skillcapped.py
    ```
    * **Note 1:** `CONCURRENT_DOWNLOADS = 10` (Adjust based on your internet speed)
    * **Note 2:** `QUALITY_PRIORITY = ["4500", "2500", "1500", "500"]` (Customize preferred resolution order)
    * **Note 3:** `FFMPEG_CHECK = True` (Set to `False` if you cannot install FFmpeg; output will be `.ts` files)

## 🗺️ Roadmap
- [x] **Quality Control:** Dynamic resolution selection with automatic fallback (Support for High/Standard Bitrate 1080p).
- [x] **Metadata:** Embeds ID3 tags (Title, Album, Track, Artist) directly into MP4 files.
- [ ] **Automation:** Auto-extract titles and crawl full courses from a single link.
- [ ] **GUI:** Simple interface for drag-and-drop.

## 🤝 Credits & Acknowledgments
* **Original Script:** This project is a modernized fork of an open-source script found on GitHub. While the original author is unknown, this project builds upon their initial logic for parsing Skill-Capped URLs.
* **Modernization:** Refactored to use `asyncio`, `aiohttp`, and strict `FFmpeg` muxing for stability and speed.

## ⚖️ Disclaimer
This script is for educational purposes only. Please respect copyright laws and the terms of service of the content providers.