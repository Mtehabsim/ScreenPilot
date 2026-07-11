import os
from pathlib import Path

APP_NAME = "ScreenPilot"
SERVER_NAME = "screen-pilot"
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
SCREENS_DIR = BASE_DIR / "screens"
# JSONL timing log: one line per tool call (see timing.py / analyze_timings.py).
TIMING_LOG = BASE_DIR / "timings.jsonl"
# JPEG by default: encodes far faster than optimized PNG and produces a much
# smaller payload (cheaper/faster for the agent to consume each turn). Override
# per-call with format="PNG" when pixel-exact detail is needed.
DEFAULT_SCREENSHOT_FORMAT = "JPEG"
JPEG_QUALITY = 70
DEFAULT_CLICK_DURATION = 0.5
# Post-action settle sleep. Kept short because pyautogui.PAUSE already spaces
# events; callers pass a larger value only when they need the UI to redraw.
DEFAULT_DELAY = 0.15
LONG_DELAY = 1.0
# Extra settle time after text entry / hotkeys before the verification
# screenshot, so menus, autocomplete popups and navigation have time to render.
# Paste is instant, so this only needs to cover UI redraw / navigation.
TYPE_SETTLE_DELAY = 0.3
# Instant mouse jumps — the animated glide added latency without reliability.
MOUSE_MOVE_DURATION = 0.0
DEFAULT_CONFIDENCE = 0.9
DEFAULT_WAIT_TIMEOUT = 10
# The scaled image the agent sees is TARGET_WIDTH px wide; height follows the
# display's true aspect ratio (see utils.get_scaling_ratio). TARGET_HEIGHT is a
# reference/advisory bound only — it no longer forces a fixed image shape, so
# screenshots are never squashed.
TARGET_WIDTH = 1366
TARGET_HEIGHT = 768

# Surfaced to MCP clients via FastMCP(instructions=...). Tells agents how to
# drive the device correctly before they touch any tool.
SERVER_INSTRUCTIONS = """\
ScreenPilot lets you see and control this device. Follow this contract:

1. ALWAYS call get_screen_info() first, before any screenshot or action. It
   returns the coordinate space you must use ("width"/"height"), the display's
   actual resolution, and the scale ratio. All x/y coordinates you pass to
   mouse_click and perform_actions MUST be in that returned coordinate space
   (read them off a see_screen() image) — never guess in physical pixels.
2. Screenshots are your ground truth. Confirm the result of an action matches
   your intent BEFORE issuing the next one. Most tools return a screenshot, so
   read THAT instead of making a separate see_screen() call.
2a. Batch to cut round-trips: for a multi-step action (e.g. moving a piece =
   click source then click destination), use ONE perform_actions call with
   take_screenshots=false and look at the single screenshot it returns at the
   end — not three separate calls.
2b. Cut round-trips with the general mechanisms:
     - open_app(name): launch/focus ANY app via the OS launcher in one call.
     - perform_actions(..., settle=true): run a batch of actions, then wait for
       the screen to STOP changing before the single returned screenshot — so a
       flow that triggers loading/navigation needs no follow-up "did it finish?"
       screenshot. This works for any app; it bakes in no app-specific behavior.
3. Text entry (keyboard_action type="type") pastes via the clipboard, so text
   appears instantly and completely — do not retype character-by-character if
   text looks missing; take a fresh screenshot to verify first.
4. Prefer typing a full URL and pressing Enter over clicking tiny targets. When
   a click misses, re-screenshot and re-read coordinates rather than nudging
   blindly.
"""