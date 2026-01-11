import customtkinter as ctk
import asyncio
import threading
import sys
from pathlib import Path
from playwright.async_api import async_playwright

# Local modules
from downloader import SkillCappedDownloader
from scraper import scrape_details
from utils import sanitize_filename, parse_title_metadata

# --- THEME SETTINGS ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class TextRedirector:
    """Redirects print() output to the GUI text box."""
    def __init__(self, widget):
        self.widget = widget

    def write(self, str_val):
        self.widget.configure(state="normal")
        self.widget.insert("end", str_val)
        self.widget.see("end")
        self.widget.configure(state="disabled")

    def flush(self):
        pass

class SkillCappedGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SkillCapped Downloader")
        self.geometry("700x600")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. HEADER
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(self.header_frame, text="SkillCapped Downloader", font=("Roboto Medium", 24)).pack(side="left")
        ctk.CTkLabel(self.header_frame, text="v2.1 | Modular Suite", font=("Roboto", 12), text_color="gray").pack(side="left", padx=10, pady=(8, 0))

        # 2. INPUT AREA
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        ctk.CTkLabel(self.input_frame, text="Paste URLs (Magic Mode supported):", font=("Roboto", 14)).pack(anchor="w", padx=15, pady=(15, 5))

        self.url_entry = ctk.CTkTextbox(self.input_frame, height=100, font=("Consolas", 12))
        self.url_entry.pack(fill="x", padx=15, pady=(0, 15))
        self.url_entry.insert("0.0", "# Paste links here (one per line)...\n")

        # 3. CONTROLS
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=5)

        ctk.CTkLabel(self.controls_frame, text="Quality Priority:", font=("Roboto", 12)).pack(side="left", padx=(0, 10))
        self.quality_var = ctk.StringVar(value="Best (1080p)")
        ctk.CTkOptionMenu(
            self.controls_frame, 
            values=["Best (1080p)", "Standard (1080p)", "Data Saver (720p)", "Low (480p)"],
            variable=self.quality_var, width=150
        ).pack(side="left")

        self.start_btn = ctk.CTkButton(self.controls_frame, text="START DOWNLOAD", font=("Roboto Medium", 14), height=40, fg_color="#1f538d", hover_color="#14375e", command=self.start_thread)
        self.start_btn.pack(side="right")

        # 4. LOG CONSOLE
        ctk.CTkLabel(self, text="Status Log:", font=("Roboto", 12, "bold")).grid(row=3, column=0, sticky="w", padx=25, pady=(10, 0))
        self.log_box = ctk.CTkTextbox(self, state="disabled", font=("Consolas", 11), fg_color="#1a1a1a", text_color="#dce4ee")
        self.log_box.grid(row=4, column=0, sticky="nsew", padx=20, pady=(5, 20))
        sys.stdout = TextRedirector(self.log_box)

    def start_thread(self):
        self.start_btn.configure(state="disabled", text="RUNNING...")
        thread = threading.Thread(target=self.run_async_process, daemon=True)
        thread.start()

    def run_async_process(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.process_downloads())
            loop.close()
        except Exception as e:
            print(f"[!] Critical Error: {e}")
        finally:
            self.start_btn.configure(state="normal", text="START DOWNLOAD")
            print("\n--- Ready for next task ---")

    async def process_downloads(self):
        raw_text = self.url_entry.get("1.0", "end")
        lines = [line.strip() for line in raw_text.split("\n") if line.strip() and not line.strip().startswith("#")]

        if not lines:
            print("[!] No URLs found.")
            return

        # Quality Mapping
        q_map = {
            "Best": ["4500", "2500", "1500", "500"],
            "Standard": ["2500", "1500", "4500", "500"],
            "Data": ["1500", "500", "2500", "4500"],
            "Low": ["500", "1500", "2500", "4500"]
        }
        priority = next((v for k, v in q_map.items() if k in self.quality_var.get()), ["4500"])
        print(f"[*] Starting batch with quality profile: {self.quality_var.get()}")

        downloader = SkillCappedDownloader(quality_priority=priority)
        playwright = await async_playwright().start()
        browser = await playwright.firefox.launch(headless=True)
        page = await browser.new_page()

        try:
            for line in lines:
                parts = line.split(",")
                # Magic Mode
                if len(parts) < 3:
                    url = parts[0].strip()
                    if not url.startswith("http"): continue
                    print(f"[*] Auto-detecting info for: {url}...")
                    course_raw, video_raw = await scrape_details(page, url)
                    if not course_raw: continue
                # Manual Mode
                else:
                    course_raw, video_raw, url = [p.strip() for p in parts]

                course_name = sanitize_filename(course_raw)
                video_name = sanitize_filename(video_raw)
                meta_title, meta_track = parse_title_metadata(video_raw)
                
                output_dir = Path(course_name)
                output_dir.mkdir(parents=True, exist_ok=True)
                
                video_id, manifest_url, _ = await downloader.find_valid_manifest(url)
                if video_id:
                    await downloader.download_video(video_id, video_name, output_dir, manifest_url, {
                        "album": course_raw, "title": meta_title, "track": meta_track
                    })
                else:
                    print(f"[!] ID not found for {url}")
            print("\n[SUCCESS] All Tasks Completed.")

        finally:
            await browser.close()
            await playwright.stop()

if __name__ == "__main__":
    app = SkillCappedGUI()
    app.mainloop()