from mcp.server.fastmcp import FastMCP
import config
from utils import ensure_directory_exists

from core.screen_capture import ScreenCapture
from core.mouse import Mouse
from core.keyboard import Keyboard
from core.scroll import Scroll
from core.element import Element
from core.action_sequence import ActionSequence


class ScreenPilot:
    
    def __init__(self):
        ensure_directory_exists(config.SCREENS_DIR)        
        self.mcp = FastMCP(config.SERVER_NAME)
        
        self.tools = [
            ScreenCapture(self.mcp, config.SCREENS_DIR),
            Mouse(self.mcp, config.SCREENS_DIR),
            Keyboard(self.mcp, config.SCREENS_DIR),
            Scroll(self.mcp, config.SCREENS_DIR),
            Element(self.mcp, config.SCREENS_DIR),
            ActionSequence(self.mcp, config.SCREENS_DIR)
        ]
        
        for tool in self.tools:
            tool.register()
    
    def run(self, transport='stdio'):
        self.mcp.run(transport=transport)


if __name__ == "__main__":
    app = ScreenPilot()
    app.run()