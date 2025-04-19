import io
import datetime
from pathlib import Path
from mcp.server.fastmcp import Image
from PIL import Image as PILImage
import pyautogui
from config import TARGET_WIDTH, TARGET_HEIGHT

def ensure_directory_exists(directory: Path) -> None:
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)

def get_scaling_ratio():
    actual_width, actual_height = pyautogui.size()
    x_ratio = TARGET_WIDTH / actual_width
    y_ratio = TARGET_HEIGHT / actual_height
    return (x_ratio, y_ratio)

def scale_image(image, target_width=TARGET_WIDTH, target_height=TARGET_HEIGHT):
    return image.resize((target_width, target_height), PILImage.LANCZOS)

def scale_coordinates(x, y, inverse=False):
    x_ratio, y_ratio = get_scaling_ratio()
    
    if inverse:
        return int(x / x_ratio), int(y / y_ratio)
    else:
        return int(x * x_ratio), int(y * y_ratio)
        
def save_screenshot_to_file(screenshot, screens_dir: Path, prefix: str, 
                           format: str = "PNG", extra_info: str = None) -> Image:
    buffer = io.BytesIO()
    screenshot = scale_image(screenshot)
    
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