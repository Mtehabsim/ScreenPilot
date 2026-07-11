import io
import sys
import datetime
import time
from pathlib import Path
from mcp.server.fastmcp import Image
from PIL import Image as PILImage
import pyautogui
import pyperclip
from config import TARGET_WIDTH, TARGET_HEIGHT, JPEG_QUALITY
from timing import section

# Clipboard-paste modifier: Cmd on macOS, Ctrl elsewhere.
PASTE_MODIFIER = "command" if sys.platform == "darwin" else "ctrl"

def ensure_directory_exists(directory: Path) -> None:
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)

def type_text(value: str) -> None:
    """Enter text reliably by pasting from the clipboard.

    Preferred over pyautogui.write(), which on macOS drops/reorders characters
    and mistimes modifier keys. Falls back to write() only if the clipboard is
    unavailable.
    """
    try:
        previous = None
        try:
            previous = pyperclip.paste()
        except Exception:
            previous = None
        pyperclip.copy(value)
        pyautogui.hotkey(PASTE_MODIFIER, "v")
        # Let the paste land before we restore the previous clipboard contents.
        time.sleep(0.15)
        if previous is not None:
            try:
                pyperclip.copy(previous)
            except Exception:
                pass
    except Exception:
        # Last-resort fallback: slow interval reduces (but can't eliminate) the
        # dropped-character problem.
        pyautogui.write(value, interval=0.02)

def get_scaling_ratio():
    """Single uniform ratio that maps the true display onto the scaled image.

    Derived from width alone and applied to BOTH axes, so the aspect ratio is
    preserved and the screenshot the agent sees is never distorted. Returns
    (ratio, ratio) to stay compatible with existing callers.
    """
    actual_width, _actual_height = pyautogui.size()
    ratio = TARGET_WIDTH / actual_width
    return (ratio, ratio)

def get_scaled_dimensions():
    """Scaled image size (width, height) preserving the display aspect ratio."""
    actual_width, actual_height = pyautogui.size()
    ratio = TARGET_WIDTH / actual_width
    return (int(actual_width * ratio), int(actual_height * ratio))

def scale_image(image):
    target_width, target_height = get_scaled_dimensions()
    return image.resize((target_width, target_height), PILImage.LANCZOS)

def scale_coordinates(x, y, inverse=False):
    ratio, _ = get_scaling_ratio()

    if inverse:
        # scaled/image space -> physical device space
        return int(x / ratio), int(y / ratio)
    else:
        # physical device space -> scaled/image space
        return int(x * ratio), int(y * ratio)
        
def save_screenshot_to_file(screenshot, screens_dir: Path, prefix: str,
                           format: str = "PNG", extra_info: str = None) -> Image:
    buffer = io.BytesIO()
    with section("scale"):
        screenshot = scale_image(screenshot)

    with section("encode"):
        if format.upper() == "JPEG":
            # quality over optimize: faster encode, small payload, fine for reading UI.
            screenshot.convert("RGB").save(buffer, format="JPEG", quality=JPEG_QUALITY)
        else:
            # optimize=False: PNG optimization is slow and rarely worth it here.
            screenshot.save(buffer, format="PNG", optimize=False)

    data = buffer.getvalue()
    with section("disk"):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        extra_part = f"_{extra_info}" if extra_info else ""
        filename = f"{prefix}{extra_part}_{timestamp}.{format.lower()}"
        filepath = screens_dir / filename
        with open(filepath, "wb") as f:
            f.write(data)

    return Image(data=data, format=format.lower())