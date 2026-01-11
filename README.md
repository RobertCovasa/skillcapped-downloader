# SkillCapped Downloader

A fast, async downloader for Skill-Capped. Automatically organizes videos into folders and muxes them into clean MP4s using FFmpeg.

## ⚡ Features
* **Fast & Resumable:** Concurrent downloads via `aiohttp`; restarts exactly where it left off.
* **High Quality:** Lossless `.ts` to `.mp4` muxing (no re-encoding).
* **Smart:** Auto-detects video IDs from URLs.

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
    Jungle Guide, 01 - Intro, URL

    # Comments are supported
    ```

2.  **Run the script:**
    ```bash
    python skillcapped.py
    ```
    *Note 1: `CONCURRENT_DOWNLOADS` = 10 (Adjust based on your internet speed)*
    *Note 2: `FFMPEG_CHECK` = True (Set to False if you cannot install FFmpeg; output will be .ts files)*

## 🗺️ Roadmap
- [ ] **Automation:** Auto-extract titles and crawl full courses from a single link.
- [ ] **Quality Control:** Dynamic resolution selection (1080p/720p).
- [ ] **Metadata:** Embed ID3 tags (Title, Album, Track) into MP4s.
- [ ] **GUI:** Simple interface for drag-and-drop.

## ⚖️ Disclaimer
This script is for educational purposes only. Please respect copyright laws and the terms of service of the content providers.