import os
from pathlib import Path

APP_NAME = "ScreenPilot"
SERVER_NAME = "screen-pilot"
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
SCREENS_DIR = BASE_DIR / "screens"
DEFAULT_SCREENSHOT_FORMAT = "PNG"
DEFAULT_CLICK_DURATION = 0.5
DEFAULT_DELAY = 0.5
LONG_DELAY = 1.0
MOUSE_MOVE_DURATION = 0.3
DEFAULT_CONFIDENCE = 0.9
DEFAULT_WAIT_TIMEOUT = 10