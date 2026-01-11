# SkillCapped Downloader

A high-speed, asynchronous downloader for Skill-Capped videos. This tool automatically organizes downloads into course folders, sanitizes filenames, and merges video segments into high-quality MP4 files.

## 🚀 Features

* **High Speed:** Uses `aiohttp` and `asyncio` to download multiple video segments simultaneously.
* **Resumable:** Smartly skips segments that have already been downloaded. If the script crashes, just run it again—it picks up exactly where it left off.
* **MP4 Muxing:** Uses FFmpeg to losslessly merge `.ts` segments into a clean `.mp4` container (no re-encoding).
* **Smart Parsing:** Automatically detects video IDs from URLs without needing a browser or Selenium.
* **Path Independent:** Works seamlessly on Windows, Linux, and macOS.

## 🛠️ Prerequisites

1.  **Python 3.8+**
2.  **FFmpeg:** This is required to merge video segments.
    * **Windows:** Download FFmpeg, extract it, and add the `bin` folder to your System PATH.
    * **Mac:** `brew install ffmpeg`
    * **Linux:** `sudo apt install ffmpeg`

## 📦 Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/yourusername/skillcapped-downloader.git](https://github.com/yourusername/skillcapped-downloader.git)
    cd skillcapped-downloader
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## 📖 How to Use

1.  **Prepare your input file:**
    Add your videos to `inputs.txt` in the following format:
    ```csv
    Course Name, Video Title, URL
    ```
    *Example:*
    ```text
    Jungle Guide, 01 - Intro, LINK
    ```

2.  **Run the downloader:**
    ```bash
    python skillcapped.py
    ```

3.  **Check your output:**
    The script will create a folder named `Jungle Guide` and place `01 - Intro.mp4` inside it.

## ⚙️ Configuration

You can tweak the following variables at the top of the script:
* `CONCURRENT_DOWNLOADS = 10` (Adjust based on your internet speed)
* `FFMPEG_CHECK = True` (Set to `False` if you cannot install FFmpeg; output will be `.ts` files)

# 🗺️ Project Roadmap & To-Do

The following features are planned to transition this project from a manual downloader to a fully automated archiving suite.

## Phase 1: Automation & Intelligence (High Priority)
- [ ] **Auto-Title Extraction**
    - *Goal:* Eliminate manual entry in `inputs.txt`.
    - *Plan:* Implement a lightweight scraper to fetch the Course Name and Video Title directly from the provided URL.
- [ ] **Course Crawling**
    - *Goal:* One link to download an entire course.
    - *Plan:* Allow users to input a "Course Overview" URL. The script will parse the page, find all associated video IDs, and queue them automatically.

## Phase 2: Core Engine Improvements
- [ ] **Dynamic Quality Selection**
    - *Goal:* Stop hardcoding `4500` (bitrate).
    - *Plan:* Parse the master `.m3u8` manifest to detect available resolutions (1080p, 720p, 480p) and let the user define a preference.
- [ ] **Smart Metadata Embedding**
    - *Goal:* Professional file output.
    - *Plan:* Use FFmpeg to embed ID3 tags (Title, Album/Course, Track Number) directly into the MP4 container. This ensures videos look organized in players like VLC.
- [ ] **Download History / Database**
    - *Goal:* Prevent redundancy.
    - *Plan:* Create a local `history.json` log. The script will check this before downloading to ensure the same video ID isn't downloaded twice.

## Phase 3: Advanced & Quality of Life
- [ ] **CLI Arguments Support**
    - *Goal:* Quick single-video downloads.
    - *Plan:* Add `argparse` to allow command-line usage: `python main.py --url "LINK" --quality 1080p`.
- [ ] **Authentication Handling**
    - *Goal:* Access premium content.
    - *Plan:* Add support for passing session cookies to access videos locked behind a subscription paywall.
- [ ] **GUI (Graphical User Interface)**
    - *Goal:* User-friendliness.
    - *Plan:* specific simple window (Tkinter/PyQt) for drag-and-drop URL processing and visual progress bars.

## 🤝 Credits & Acknowledgments

* **Original Script:** This project is a modernized fork of an open-source script found on GitHub. While the original author is unknown, this project builds upon their initial logic for parsing Skill-Capped URLs.
* **Modernization:** Refactored to use `asyncio`, `aiohttp`, and strict `FFmpeg` muxing for stability and speed.

## ⚖️ Disclaimer

This script is for **educational purposes only**. Please respect copyright laws and the terms of service of the content providers.