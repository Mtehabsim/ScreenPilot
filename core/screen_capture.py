import pyautogui
from typing import Dict, Any
from .base_tool import BaseTool
from mcp.server.fastmcp import Image


class ScreenCapture(BaseTool):
    """
    Provides functionality for capturing the screen.
    """
    
    def register(self):
        """Register screen capture tools with the MCP server."""
        self.mcp.tool()(self.see_screen)
        self.mcp.tool()(self.get_screen_info)
    
    async def see_screen(self, format: str = "PNG") -> Image:
        """
        Takes a screenshot and returns it as an Image object.
        
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
        
        Returns:
            Dictionary containing screen width, height, and current mouse position
        """
        try:
            width, height = pyautogui.size()
            x, y = pyautogui.position()
            return {
                "width": width,
                "height": height,
                "current_mouse_position": [x, y]
            }
        except Exception as e:
            return self.handle_exception(e, "get screen info")