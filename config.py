# --- CONFIGURATION ---
CONCURRENT_DOWNLOADS = 10
FFMPEG_CHECK = True

# Quality Priority List: The script tries these in order.
# 4500 = 1080p @ 60fps (Best)
# 2500 = 1080p @ 60fps (Standard)
# 1500 = 720p  @ 30fps (Medium)
# 500  = 480p  @ 30fps (Low)
DEFAULT_PRIORITY = ["4500", "2500", "1500", "500"]