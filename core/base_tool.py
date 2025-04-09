from abc import ABC
from typing import Dict, Any, Optional
from mcp.server.fastmcp import Image
import time


class BaseTool(ABC):
    """
    Abstract base class for all screen interaction tools.
    Provides common functionality and defines the interface that all tools must implement.
    """
    
    def __init__(self, mcp_server, screens_dir):
        self.mcp = mcp_server
        self.screens_dir = screens_dir

    def register(self):
        pass
        
    @staticmethod
    def add_delay(seconds: float = 0.5):
        time.sleep(seconds)
        
    def save_screenshot(self, screenshot, prefix: str, format: str = "PNG", 
                        extra_info: Optional[str] = None) -> Image:
        """
        Save a screenshot to file and return it as an Image object.
        
        Args:
            screenshot: PIL Image object
            prefix: Prefix for the filename
            format: Format of the screenshot ("PNG" or "JPEG")
            extra_info: Additional information to include in the filename
        
        Returns:
            Image object
        """
        from utils import save_screenshot_to_file
        return save_screenshot_to_file(
            screenshot, 
            self.screens_dir, 
            prefix, 
            format, 
            extra_info
        )
        
    def format_result(self, status: str, screenshot=None) -> Dict[str, Any]:
        result = {"status": status}
        if screenshot:
            result["screenshot"] = screenshot
        return result
        
    def handle_exception(self, e: Exception, operation: str) -> Dict[str, str]:
        error_msg = f"Error performing {operation}: {str(e)}"
        return {"error": error_msg}