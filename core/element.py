import pyautogui
import time
from typing import Dict, Any
from .base_tool import BaseTool


class Element(BaseTool):
    """
    Provides functionality for detecting and waiting for elements on screen.
    """
    
    def register(self):
        self.mcp.tool()(self.element_exists)
        self.mcp.tool()(self.wait_for_element)
    
    async def element_exists(self, image_path: str, confidence: float = 0.9) -> Dict[str, Any]:
        """
        Checks if a specific element exists on screen by comparing with an image.
        
        Args:
            image_path: Path to the image file to search for
            confidence: Confidence level for the match (0.0 to 1.0)
        
        Returns:
            Dictionary with existence status and location if found
        """
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                return {
                    "exists": True,
                    "location": {
                        "left": location.left,
                        "top": location.top,
                        "width": location.width,
                        "height": location.height
                    }
                }
            else:
                return {"exists": False}
        except Exception as e:
            return self.handle_exception(e, "element detection")
    
    async def wait_for_element(self, image_path: str, max_wait_seconds: int = 10, 
                              confidence: float = 0.9) -> Dict[str, Any]:
        """
        Waits for a specific element to appear on screen by comparing with an image.
        
        Args:
            image_path: Path to the image file to search for
            max_wait_seconds: Maximum time to wait in seconds
            confidence: Confidence level for the match (0.0 to 1.0)
        
        Returns:
            Dictionary with success status and location if found
        """
        try:
            start_time = time.time()
            while time.time() - start_time < max_wait_seconds:
                location = pyautogui.locateOnScreen(image_path, confidence=confidence)
                if location:
                    return {
                        "success": True,
                        "time_taken": time.time() - start_time,
                        "location": {
                            "left": location.left,
                            "top": location.top,
                            "width": location.width,
                            "height": location.height
                        }
                    }
                time.sleep(0.5)
            
            return {
                "success": False,
                "message": f"Element not found within {max_wait_seconds} seconds"
            }
        except Exception as e:
            return self.handle_exception(e, "waiting for element")