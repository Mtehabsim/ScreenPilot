import pyautogui
import time
from typing import Dict, Any
from .base_tool import BaseTool


class Scroll(BaseTool):
    """
    Provides functionality for scrolling.
    """
    
    def register(self):
        self.mcp.tool()(self.scroll)
        self.mcp.tool()(self.scroll_to_position)
    
    async def scroll(self, direction: str = "down", amount: int = 300, 
                    take_screenshot: bool = True, format: str = "PNG") -> Dict[str, Any]:
        """
        Scrolls the screen in the specified direction by the given amount.
        
        Args:
            direction: Direction to scroll ("up", "down", "left", "right", "top", "bottom")
            amount: Number of pixels to scroll (ignored for "top" and "bottom")
            take_screenshot: Whether to take a screenshot after scrolling (default: True)
            format: Format of the screenshot ("PNG" or "JPEG")
        
        Returns:
            Dictionary with status message and screenshot if requested
        """
        try:
            direction = direction.lower()
            status = ""
            
            if direction == "up":
                pyautogui.scroll(amount)
                status = f"Scrolled up by {amount} pixels"
            elif direction == "down":
                pyautogui.scroll(-amount)
                status = f"Scrolled down by {amount} pixels"
            elif direction == "left":
                pyautogui.hscroll(-amount)
                status = f"Scrolled left by {amount} pixels"
            elif direction == "right":
                pyautogui.hscroll(amount)
                status = f"Scrolled right by {amount} pixels"
            elif direction == "top":
                pyautogui.hotkey('home')
                status = "Scrolled to top of page"
            elif direction == "bottom":
                pyautogui.hotkey('end')
                status = "Scrolled to bottom of page"
            else:
                return {"error": f"Unknown scroll direction: {direction}. Use 'up', 'down', 'left', 'right', 'top', or 'bottom'."}
            
            self.add_delay()
            
            if take_screenshot:
                screenshot = pyautogui.screenshot()
                screenshot_obj = self.save_screenshot(
                    screenshot, 
                    "scroll", 
                    format, 
                    direction
                )
                return self.format_result(status, screenshot_obj)
            
            return self.format_result(status)
            
        except Exception as e:
            return self.handle_exception(e, "scroll action")
    
    async def scroll_to_position(self, percent: float = 50, 
                               take_screenshot: bool = True, format: str = "PNG") -> Dict[str, Any]:
        """
        Scrolls the screen to a specific position based on a percentage of the document length.
        
        Args:
            percent: Position to scroll to (0-100, where 0 is top and 100 is bottom)
            take_screenshot: Whether to take a screenshot after scrolling (default: True)
            format: Format of the screenshot ("PNG" or "JPEG")
        
        Returns:
            Dictionary with status message and screenshot if requested
        """
        try:
            if percent < 0 or percent > 100:
                return {"error": "Percent value must be between 0 and 100"}
                
            pyautogui.hotkey('home')
            time.sleep(0.5)
            
            if percent > 0:
                pyautogui.hotkey('end')
                time.sleep(0.5)
                
                pyautogui.hotkey('home')
                time.sleep(0.5)
                
                # This is approximate and may not work perfectly in all applications
                if percent > 0:
                    screen_height = pyautogui.size()[1]
                    estimated_doc_height = screen_height * 5
                    scroll_pixels = -int((estimated_doc_height * percent) / 100)
                    pyautogui.scroll(scroll_pixels)
            
            status = f"Scrolled to approximately {percent}% of document"
            self.add_delay(1.0)
            
            if take_screenshot:
                screenshot = pyautogui.screenshot()
                screenshot_obj = self.save_screenshot(
                    screenshot, 
                    "scroll_pos", 
                    format, 
                    str(percent)
                )
                return self.format_result(status, screenshot_obj)
            
            return self.format_result(status)
            
        except Exception as e:
            return self.handle_exception(e, "scroll to position")