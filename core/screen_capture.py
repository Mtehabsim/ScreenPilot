import pyautogui
from typing import Dict, Any
from .base_tool import BaseTool
from mcp.server.fastmcp import Image
from utils import scale_coordinates
from config import TARGET_WIDTH, TARGET_HEIGHT


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
            return "Use the available tools to help with my tasks. For optimal results, always start by getting device information with get_screen_info() before taking screenshots. This ensures proper scaling and positioning. After checking screen details, take screenshots to verify each interaction. You have full access to this device to help serve me and complete the required tasks."
            
    async def see_screen(self, format: str = "PNG") -> Image:
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
            screenshot = pyautogui.screenshot()
            return self.save_screenshot(screenshot, "screenshot", format)
            
        except Exception as e:
            raise RuntimeError(f"Screenshot failed: {str(e)}")
    
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
            
            # Scale mouse position to target resolution
            scaled_x, scaled_y = scale_coordinates(actual_x, actual_y)
            
            return {
                # "actual_width": actual_width,
                # "actual_height": actual_height,
                "width": TARGET_WIDTH,
                "height": TARGET_HEIGHT,
                "current_mouse_position": [scaled_x, scaled_y],
                "actual_mouse_position": [actual_x, actual_y]
            }
        except Exception as e:
            return self.handle_exception(e, "get screen info")