import io
import datetime
from pathlib import Path
from mcp.server.fastmcp import Image
from pathlib import Path

def ensure_directory_exists(directory: Path) -> None:
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
        
def save_screenshot_to_file(screenshot, screens_dir: Path, prefix: str, 
                           format: str = "PNG", extra_info: str = None) -> Image:
    buffer = io.BytesIO()
    if format.upper() == "JPEG":
        screenshot.convert("RGB").save(buffer, format="JPEG", optimize=True)
    else:
        screenshot.save(buffer, format="PNG", optimize=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    extra_part = f"_{extra_info}" if extra_info else ""
    filename = f"{prefix}{extra_part}_{timestamp}.{format.lower()}"
    filepath = screens_dir / filename
    
    with open(filepath, "wb") as f:
        f.write(buffer.getvalue())
    
    buffer.seek(0)
    return Image(data=buffer.getvalue(), format=format.lower())