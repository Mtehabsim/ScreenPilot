import pyautogui
from typing import Dict, Any
from .base_tool import BaseTool


class Mouse(BaseTool):

    def register(self):
        self.mcp.tool()(self.mouse_click)
    
    async def mouse_click(self, x: int, y: int, button: str = "left", clicks: int = 1, 
                          take_screenshot: bool = True, format: str = "PNG") -> Dict[str, Any]:
        """
        Moves the mouse to the specified coordinates, performs a click, and optionally takes a screenshot.
        
        Args:
            x: X-coordinate on screen
            y: Y-coordinate on screen
            button: Mouse button to click ("left", "right", or "middle")
            clicks: Number of clicks to perform (default: 1)
            take_screenshot: Whether to take a screenshot after the action (default: True)
            format: Format of the screenshot ("PNG" or "JPEG")
        
        Returns:
            Dictionary with status message and screenshot if requested
        """
        try:
            pyautogui.moveTo(x, y, duration=0.5)
            pyautogui.click(x=x, y=y, button=button, clicks=clicks)
            
            self.add_delay()
            
            status = f"Successfully clicked at position ({x}, {y}) with {button} button {clicks} time(s)"
            
            if take_screenshot:
                screenshot = pyautogui.screenshot()
                screenshot_obj = self.save_screenshot(
                    screenshot, 
                    "click", 
                    format, 
                    f"{x}_{y}"
                )
                return self.format_result(status, screenshot_obj)
            
            return self.format_result(status)
            
        except Exception as e:
            return self.handle_exception(e, "mouse click")