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

## 🤝 Credits & Acknowledgments

* **Original Script:** This project is a modernized fork of an open-source script found on GitHub. While the original author is unknown, this project builds upon their initial logic for parsing Skill-Capped URLs.
* **Modernization:** Refactored to use `asyncio`, `aiohttp`, and strict `FFmpeg` muxing for stability and speed.

## ⚖️ Disclaimer

This script is for **educational purposes only**. Please respect copyright laws and the terms of service of the content providers.