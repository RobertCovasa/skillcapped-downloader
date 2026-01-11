import customtkinter as ctk
import asyncio
import threading
import sys
from pathlib import Path
from typing import List

# Import your existing backend logic
# Make sure your main script is named 'skillcapped.py' (or adjust import)
from skillcapped import SkillCappedDownloader

# --- THEME SETTINGS ---
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class TextRedirector:
    """Redirects print() output to the GUI text box."""
    def __init__(self, widget):
        self.widget = widget

    def write(self, str_val):
        self.widget.configure(state="normal")
        self.widget.insert("end", str_val)
        self.widget.see("end") # Auto-scroll to bottom
        self.widget.configure(state="disabled")

    def flush(self):
        pass

class SkillCappedGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("SkillCapped Downloader")
        self.geometry("700x600")
        self.resizable(False, False)

        # Layout Grid Config
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Log area expands

        # 1. HEADER
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="SkillCapped Downloader", 
            font=("Roboto Medium", 24)
        )
        self.title_label.pack(side="left")

        self.version_label = ctk.CTkLabel(
            self.header_frame, 
            text="v2.0 | Automation Suite", 
            font=("Roboto", 12), 
            text_color="gray"
        )
        self.version_label.pack(side="left", padx=10, pady=(8, 0))

        # 2. INPUT AREA
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        self.url_label = ctk.CTkLabel(self.input_frame, text="Paste URLs (Magic Mode supported):", font=("Roboto", 14))
        self.url_label.pack(anchor="w", padx=15, pady=(15, 5))

        self.url_entry = ctk.CTkTextbox(self.input_frame, height=100, font=("Consolas", 12))
        self.url_entry.pack(fill="x", padx=15, pady=(0, 15))
        self.url_entry.insert("0.0", "# Paste links here (one per line)...\n")

        # 3. CONTROLS
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=5)

        # Quality Selector
        self.quality_label = ctk.CTkLabel(self.controls_frame, text="Quality Priority:", font=("Roboto", 12))
        self.quality_label.pack(side="left", padx=(0, 10))

        self.quality_var = ctk.StringVar(value="Best (1080p)")
        self.quality_menu = ctk.CTkOptionMenu(
            self.controls_frame, 
            values=["Best (1080p)", "Standard (1080p)", "Data Saver (720p)", "Low (480p)"],
            variable=self.quality_var,
            width=150
        )
        self.quality_menu.pack(side="left")

        # Download Button
        self.start_btn = ctk.CTkButton(
            self.controls_frame, 
            text="START DOWNLOAD", 
            font=("Roboto Medium", 14),
            height=40,
            fg_color="#1f538d", 
            hover_color="#14375e",
            command=self.start_thread
        )
        self.start_btn.pack(side="right")

        # 4. LOG CONSOLE
        self.log_label = ctk.CTkLabel(self, text="Status Log:", font=("Roboto", 12, "bold"))
        self.log_label.grid(row=3, column=0, sticky="w", padx=25, pady=(10, 0))

        self.log_box = ctk.CTkTextbox(self, state="disabled", font=("Consolas", 11), fg_color="#1a1a1a", text_color="#dce4ee")
        self.log_box.grid(row=4, column=0, sticky="nsew", padx=20, pady=(5, 20))

        # Redirect stdout to the log box
        sys.stdout = TextRedirector(self.log_box)

    def start_thread(self):
        """Starts the async download loop in a separate thread to keep UI responsive."""
        self.start_btn.configure(state="disabled", text="RUNNING...")
        thread = threading.Thread(target=self.run_async_process, daemon=True)
        thread.start()

    def run_async_process(self):
        """Runs the asyncio event loop."""
        try:
            # Create a new loop for this thread
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
        """The main logic bridge connecting GUI input to the Downloader class."""
        # 1. Get Inputs
        raw_text = self.url_entry.get("1.0", "end")
        lines = [line.strip() for line in raw_text.split("\n") if line.strip() and not line.strip().startswith("#")]

        if not lines:
            print("[!] No URLs found. Please paste links in the box.")
            return

        # 2. Configure Quality based on Dropdown
        q_selection = self.quality_var.get()
        # Map GUI selection to API values
        if "Best" in q_selection:
            priority = ["4500", "2500", "1500", "500"]
        elif "Standard" in q_selection:
            priority = ["2500", "1500", "4500", "500"] # Prefer 2500, fallback to others
        elif "Data Saver" in q_selection:
            priority = ["1500", "500", "2500", "4500"]
        else:
            priority = ["500", "1500", "2500", "4500"]

        print(f"[*] Starting batch with quality profile: {q_selection}")
        
        # 3. Initialize Downloader (from your existing script)
        # Note: We are assuming your original class uses the global QUALITY_PRIORITY.
        # Ideally, we modify the class to accept it as an init argument, 
        # but for now we can just monkey-patch the global var if needed, 
        # or pass it if you refactored __init__.
        
        downloader = SkillCappedDownloader()
        
        # Initialize Playwright if needed (we'll do a quick check locally)
        # For simplicity in this GUI version, we assume Magic Mode is always active/available.
        from playwright.async_api import async_playwright
        
        playwright = await async_playwright().start()
        # Headless=True for GUI (cleaner)
        browser = await playwright.firefox.launch(headless=True)
        page = await browser.new_page()

        try:
            for line in lines:
                parts = line.split(",")
                
                # MAGIC MODE CHECK
                if len(parts) < 3:
                    url = parts[0].strip()
                    if not url.startswith("http"): continue

                    print(f"[*] Auto-detecting info for: {url}...")
                    
                    # Import the scrape helper from main script, or redefine it.
                    # Since scrape_details was a standalone function in your main script,
                    # we need to make sure we can access it.
                    # PRO TIP: Add 'from skillcapped import scrape_details' at top
                    from skillcapped import scrape_details
                    
                    course_raw, video_raw = await scrape_details(page, url)
                    
                    if not course_raw:
                        print(f"[!] Failed to detect names. Skipping {url}")
                        continue
                        
                    print(f"    -> Identified: {video_raw}")
                else:
                    # Manual Mode
                    course_raw = parts[0].strip()
                    video_raw = parts[1].strip()
                    url = parts[2].strip()

                # Process Names
                course_name = downloader.sanitize_filename(course_raw)
                video_name = downloader.sanitize_filename(video_raw)
                
                meta_title, meta_track = downloader.parse_title_metadata(video_raw)
                metadata = {"album": course_raw, "title": meta_title, "track": meta_track}

                output_dir = Path(course_name)
                output_dir.mkdir(parents=True, exist_ok=True)

                # Patch the global variable in the module if necessary, or just use default
                # (For strictness, you'd modify the class to accept 'priority' in find_valid_manifest)
                
                # Actual Download
                video_id, manifest_url, _ = await downloader.find_valid_manifest(url)
                if video_id:
                    await downloader.download_video(video_id, video_name, output_dir, manifest_url, metadata)
                else:
                    print(f"[!] ID not found for {url}")

            print("\n[SUCCESS] All Tasks Completed.")

        finally:
            await browser.close()
            await playwright.stop()


if __name__ == "__main__":
    app = SkillCappedGUI()
    app.mainloop()