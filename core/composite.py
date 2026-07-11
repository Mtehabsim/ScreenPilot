"""Composite tools: collapse a common multi-step flow into one round-trip.

Rationale (from timing data): ~98% of blocking time is the agent loop, so each
tool call the agent DOESN'T have to make is the biggest possible win.

Scope note: ScreenPilot is a general device controller, not a browser tool. The
only composite here is open_app — launching an app by name via the OS launcher
is app-agnostic and useful for any task. For everything else, the general
primitives (mouse_click, keyboard_action, scroll) and perform_actions(settle=true)
already batch and settle any app's UI without baking in app assumptions.

Cross-platform: only the launcher keystroke differs per OS, isolated in
_open_launcher() with a clear fallback.
"""
import sys
import time
import pyautogui
from typing import Dict, Any

from .base_tool import BaseTool
from utils import type_text
from perception import capture_when_stable
from timing import timed_tool, section
from config import DEFAULT_SCREENSHOT_FORMAT

IS_MAC = sys.platform == "darwin"


class Composite(BaseTool):
    """High-level flows built from the primitive actions."""

    def register(self):
        self.mcp.tool()(self.open_app)

    def _settled_screenshot(self, prefix: str, format: str, timeout: float = 6.0):
        """Wait for the screen to stop changing, then save one screenshot."""
        screenshot, info = capture_when_stable(timeout=timeout)
        screenshot_obj = self.save_screenshot(screenshot, prefix, format)
        return screenshot_obj, info

    def _open_launcher(self):
        """Open the OS app launcher. Isolated so the rest stays cross-platform.

        Returns True if a launcher was opened, False if unsupported on this OS
        (caller then reports gracefully instead of doing something surprising).
        """
        if IS_MAC:
            pyautogui.hotkey("command", "space")  # Spotlight
            return True
        if sys.platform.startswith("win"):
            pyautogui.press("win")  # Start menu search
            return True
        # Linux desktops vary too much for a safe default.
        return False

    def _launch_via_os(self, name: str) -> bool:
        """Open the OS launcher and select `name`.

        Returns False if the platform has no supported launcher.
        """
        if not self._open_launcher():
            return False
        time.sleep(0.4)   # let the launcher UI appear
        type_text(name)
        time.sleep(0.4)   # let it resolve the top hit
        pyautogui.press("enter")
        return True

    @timed_tool
    async def open_app(self, app_name: str,
                       format: str = DEFAULT_SCREENSHOT_FORMAT) -> Dict[str, Any]:
        """
        Launch/focus an application by name in ONE call via the OS launcher
        (Spotlight on macOS, Start menu on Windows). Waits until the app window
        settles, then returns one screenshot.

        Works for any application (browser, editor, terminal, native app, ...).

        Args:
            app_name: Application name to search for (e.g. "Google Chrome").
            format: Screenshot format ("PNG" or "JPEG").
        """
        try:
            with section("action"):
                if not self._launch_via_os(app_name):
                    return {"error": (f"open_app is not supported on platform "
                                      f"'{sys.platform}'. Launch the app another way, "
                                      f"then use see_screen/mouse_click.")}

            screenshot_obj, info = self._settled_screenshot("open_app", format, timeout=8.0)
            status = f"Opened app: {app_name}" + ("" if info["stabilized"] else " (still loading at timeout)")
            result = self.format_result(status, screenshot_obj)
            result["settle"] = info
            return result
        except Exception as e:
            return self.handle_exception(e, "open app")
