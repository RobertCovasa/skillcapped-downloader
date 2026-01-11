# SkillCapped Downloader Suite

A modular tool to download Skill-Capped videos. Supports "Magic Mode" (URL-only detection), metadata embedding, and 1080p quality.

## ⚡ Features
* **Dual Mode:** Run via **GUI** or **CLI** (Terminal).
* **Magic Mode:** Paste a URL, and the tool auto-scrapes the Course and Video name.
* **Professional Organization:** Auto-folders, ID3 Metadata, and clean filenames.

## 📂 Project Structure
* `gui.py`: **Main Application** (Visual Interface).
* `cli.py`: Command Line Interface (for bulk processing via text file).
* `downloader.py`: Core logic engine.
* `scraper.py`: Playwright automation logic.
* `utils.py` & `config.py`: Helpers and settings.

## 🛠️ Setup
1.  **Install Python 3.8+** & **FFmpeg**.
2.  **Install Requirements:**
    ```bash
    pip install -r requirements.txt
    playwright install firefox
    ```

## 🚀 How to Use

### Option A: The GUI (Recommended)
1.  Run the interface:
    ```bash
    python gui.py
    ```
2.  **Paste Links:** You can paste bare URLs (Magic Mode) or `Course, Title, URL`.
3.  **Select Quality:** Choose "Best", "Standard", or "Data Saver".
4.  **Click Start.**

### Option B: The CLI (Text File)
1.  Open `inputs.txt` and add your links:
    ```text
    https://www.skill-capped.com/lol/browse/course/123/456
    ```
2.  Run the script:
    ```bash
    python cli.py
    ```