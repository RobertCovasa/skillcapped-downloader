# SkillCapped Downloader

A fast, async downloader for Skill-Capped. This tool automatically organizes videos into course folders, embeds metadata, and parses video titles directly from URLs—no manual naming required.

## ⚡ Features
* **Fast & Resumable:** Concurrent downloads via `aiohttp`; restarts exactly where it left off.
* **Magic Mode:** Simply paste a URL. The script uses a headless browser to auto-detect the **Course Name** and **Video Title** for you.
* **Adaptive Quality:** Automatically prioritizes **1080p @ 60fps (High Bitrate)**. If unavailable, it falls back to Standard 1080p, 720p, or 480p so downloads never fail.
* **Professional Metadata:** Embeds ID3 tags (Title, Album/Course, Track Number) directly into the MP4s for clean organization in media players.
* **High Quality Output:** Lossless `.ts` to `.mp4` muxing (no re-encoding).

## 🛠️ Setup

1.  **Install Python 3.8+**
2.  **Install FFmpeg:** Ensure `ffmpeg` is accessible in your system PATH.
3.  **Install Dependencies:**
    ```bash
    git clone [https://github.com/yourusername/skillcapped-downloader.git](https://github.com/yourusername/skillcapped-downloader.git)
    cd skillcapped-downloader
    pip install -r requirements.txt
    ```
4.  **Install Browser Engine (Required for Magic Mode):**
    ```bash
    playwright install firefox
    ```

## 🚀 Usage

1.  **Configure `inputs.txt`:**
    You can mix and match two formats in the file:

    * **Method 1: Magic Mode (URL Only)**
        * Just paste the link. The script will scrape the site for the Course and Video names.
    * **Method 2: Manual Override**
        * Format: `Course Name, Video Title, URL` (Useful if you want custom folder names).

    **Example `inputs.txt`:**
    ```text
    # --- Magic Mode ---
    [https://www.skill-capped.com/lol/browse/course/123/456](https://www.skill-capped.com/lol/browse/course/123/456)

    # --- Manual Override ---
    Jungle Guide, 01 - Intro, [https://www.skill-capped.com/lol/browse/course/123/456](https://www.skill-capped.com/lol/browse/course/123/456)
    ```

2.  **Run the script:**
    ```bash
    python skillcapped.py
    ```

### ⚙️ Configuration (Optional)
You can tweak these variables at the top of the script:
* `CONCURRENT_DOWNLOADS = 10` (Adjust based on your internet speed).
* `QUALITY_PRIORITY` (Customize preference order, e.g., prefer 720p to save space).
* `FFMPEG_CHECK = True` (Set to `False` if you cannot install FFmpeg; output will be `.ts` files).

## 🗺️ Roadmap
- [x] **Quality Control:** Dynamic resolution selection with automatic fallback (Support for High/Standard Bitrate 1080p).
- [x] **Metadata:** Embed ID3 tags (Title, Album, Track, Artist) directly into MP4 files.
- [x] **Auto-Title Extraction:** "Magic Mode" scrapes Course and Video names via Playwright.
- [ ] **GUI:** Simple interface for drag-and-drop.

## 🤝 Credits & Acknowledgments
* **Original Script:** This project is a modernized fork of the script by **mrhappyasthma**. This project builds upon their initial logic for parsing Skill-Capped URLs.
* **Modernization:** Refactored to use `asyncio`, `aiohttp`, `playwright`, and strict `FFmpeg` muxing for stability and speed.

## ⚖️ Disclaimer
This script is for educational purposes only. Please respect copyright laws and the terms of service of the content providers.