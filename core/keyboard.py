import pyautogui
from typing import Dict, Any
from .base_tool import BaseTool
from utils import type_text
from config import TYPE_SETTLE_DELAY, DEFAULT_SCREENSHOT_FORMAT
from timing import timed_tool, section


class Keyboard(BaseTool):

    def register(self):
        self.mcp.tool()(self.keyboard_action)

    @timed_tool
    async def keyboard_action(self, action_type: str, value: str,
                             take_screenshot: bool = True, format: str = DEFAULT_SCREENSHOT_FORMAT) -> Dict[str, Any]:
        """
        Performs a keyboard action and optionally takes a screenshot.

        Args:
            action_type: Type of action ("type" for text input, "press" for key press, or "hotkey" for combinations)
            value: Text to type or key to press (for hotkey, use format like "ctrl+t")
            take_screenshot: Whether to take a screenshot after the action (default: True)
            format: Format of the screenshot ("PNG" or "JPEG")

        Returns:
            Dictionary with status message and screenshot if requested
        """
        try:
            status = ""
            settle = None  # extra settle time before the verification screenshot
            action_type = action_type.lower()

            with section("action"):
                if action_type == "type":
                    # Paste via clipboard instead of synthesizing per-character key
                    # events. pyautogui.write() on macOS drops/reorders characters and
                    # mistimes modifier keys (e.g. Shift for ':'), which corrupts input
                    # like URLs and can trigger stray shortcuts. Paste is instant and exact.
                    type_text(value)
                    settle = TYPE_SETTLE_DELAY
                    status = f"Successfully typed: {value}"
                elif action_type == "press":
                    pyautogui.press(value)
                    status = f"Successfully pressed key: {value}"
                elif action_type == "hotkey":
                    # Split the value by '+' to get individual keys
                    keys = [k.strip() for k in value.split('+')]
                    pyautogui.hotkey(*keys)
                    settle = TYPE_SETTLE_DELAY
                    status = f"Successfully pressed hotkey combination: {value}"
                else:
                    return {"error": f"Unknown action type: {action_type}. Use 'type', 'press', or 'hotkey'."}

            self.add_delay()
            if settle:
                self.add_delay(settle)

            if take_screenshot:
                screenshot = self.capture_screenshot()
                screenshot_obj = self.save_screenshot(
                    screenshot, 
                    f"keyboard_{action_type}", 
                    format
                )
                return self.format_result(status, screenshot_obj)
            
            return self.format_result(status)
            
        except Exception as e:
            return self.handle_exception(e, "keyboard action")