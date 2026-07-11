import pyautogui
from typing import Dict, Any
from .base_tool import BaseTool
from mcp.server.fastmcp import Image
from utils import scale_coordinates, get_scaled_dimensions, get_scaling_ratio
from config import TARGET_WIDTH, TARGET_HEIGHT, DEFAULT_SCREENSHOT_FORMAT
from timing import timed_tool


class ScreenCapture(BaseTool):
    """
    Provides functionality for capturing the screen.
    """
    
    def register(self):
        """Register screen capture tools with the MCP server."""
        self.mcp.tool()(self.see_screen)
        self.mcp.tool()(self.get_screen_info)

        @self.mcp.prompt()
        def use_my_device() -> str:
            """Provides guidance on proper device interaction sequence."""
            return (
                "You have full access to this device to complete my tasks. Work in this loop:\n"
                "1. FIRST call get_screen_info() to learn the coordinate space "
                "('width'/'height'), the display's actual resolution, and the scale ratio. "
                "Do this before any screenshot or action.\n"
                "2. Call see_screen() to look. Every x/y you pass to mouse_click or "
                "perform_actions MUST be read off that image in the get_screen_info() "
                "coordinate space — never guess physical pixels.\n"
                "3. After EACH action, call see_screen() again and confirm it did what you "
                "intended before the next action.\n"
                "4. To enter text, use keyboard_action type='type' — it pastes via the "
                "clipboard, so text appears instantly and completely. If text looks missing, "
                "re-screenshot to verify before retyping.\n"
                "5. Prefer typing a full URL + Enter over clicking small targets. If a click "
                "misses, re-screenshot and re-read coordinates instead of nudging blindly."
            )
            
    @timed_tool
    async def see_screen(self, format: str = DEFAULT_SCREENSHOT_FORMAT) -> Image:
        """
        Takes a screenshot and returns it as an Image object.
        The image will be scaled to the target resolution (1366x768).
        Request device info before using this tool.
        Args:
            format: Format of the screenshot ("PNG" or "JPEG")

        Returns:
            Image object
        """
        try:
            screenshot = self.capture_screenshot()
            return self.save_screenshot(screenshot, "screenshot", format)

        except Exception as e:
            raise RuntimeError(f"Screenshot failed: {str(e)}")

    @timed_tool
    async def get_screen_info(self) -> Dict[str, Any]:
        """
        Gets information about the screen resolution and mouse position.
        Returns values scaled to the target resolution (1366x768).
        
        Returns:
            Dictionary containing screen width, height, and current mouse position
        """
        try:
            actual_width, actual_height = pyautogui.size()
            actual_x, actual_y = pyautogui.position()

            # The coordinate space you must use: the scaled-image dimensions,
            # which preserve the display's aspect ratio (no distortion).
            width, height = get_scaled_dimensions()
            ratio, _ = get_scaling_ratio()

            # Scale mouse position into that coordinate space.
            scaled_x, scaled_y = scale_coordinates(actual_x, actual_y)

            return {
                # Use these for all mouse_click / perform_actions coordinates:
                "width": width,
                "height": height,
                "current_mouse_position": [scaled_x, scaled_y],
                # The display's true resolution and the mapping, for reference:
                "actual_width": actual_width,
                "actual_height": actual_height,
                "actual_mouse_position": [actual_x, actual_y],
                "scale_ratio": round(ratio, 5),
                "coordinate_space_note": (
                    "Pass x/y in width x height space (read off see_screen images). "
                    "They are scaled by 1/scale_ratio to reach physical pixels."
                ),
            }
        except Exception as e:
            return self.handle_exception(e, "get screen info")
