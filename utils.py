import re
from typing import Tuple, Optional

def sanitize_filename(name: str) -> str:
    """Removes characters that are illegal in Windows filenames."""
    clean = re.sub(r'[<>:"/\\|?*]', '', name)
    return clean.strip().rstrip('.')

def parse_title_metadata(video_name: str) -> Tuple[str, Optional[str]]:
    """
    Extracts track number and clean title from strings like '01 - Intro'.
    Returns: (Clean Title, Track Number)
    """
    match = re.match(r'^(\d+)[ .-]+(.*)', video_name)
    if match:
        track_num = match.group(1)
        clean_title = match.group(2).strip()
        return clean_title, track_num
    return video_name, None