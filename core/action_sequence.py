import pyautogui
import time
from typing import Dict, Any, List
from .base_tool import BaseTool


class ActionSequence(BaseTool):
    """
    Provides functionality for performing sequences of actions.
    """
    
    def register(self):
        self.mcp.tool()(self.perform_actions)
    
    async def perform_actions(self, actions: List[Dict[str, Any]], take_screenshots: bool = True, 
                             format: str = "PNG") -> Dict[str, Any]:
        """
        Performs a sequence of mouse and keyboard actions.
        
        Args:
            actions: List of action dictionaries, each containing:
                    - 'type': 'mouse_click', 'keyboard', or 'scroll'
                    - For mouse_click: 'x', 'y', 'button' (optional), 'clicks' (optional)
                    - For keyboard: 'action_type' ('type', 'press', or 'hotkey'), 'value'
                    - For scroll: 'direction', 'amount' (optional)
            take_screenshots: Whether to take screenshots after each action (default: True)
            format: Format of the screenshots ("PNG" or "JPEG")
        
        Returns:
            Dictionary with results of each action and final screenshot
        """
        try:
            results = []
            
            for i, action in enumerate(actions):
                
                action_type = action.get("type", "")
                
                if action_type == "mouse_click":
                    result = await self._handle_mouse_click(action)
                    results.append(result)
                
                elif action_type == "keyboard":
                    result = await self._handle_keyboard_action(action)
                    results.append(result)
                
                elif action_type == "scroll":
                    result = await self._handle_scroll_action(action)
                    results.append(result)
                
                else:
                    results.append({
                        "action": action_type,
                        "status": "error",
                        "message": f"Unknown action type: {action_type}"
                    })
                    continue
                
                self.add_delay(0.5)
            
            response = {"results": results}
            
            if take_screenshots:
                self.add_delay(0.5)
                screenshot = pyautogui.screenshot()
                screenshot_obj = self.save_screenshot(
                    screenshot, 
                    "actions_sequence", 
                    format
                )
                response["screenshot"] = screenshot_obj
            
            return response
            
        except Exception as e:
            return self.handle_exception(e, "actions sequence")
    
    async def _handle_mouse_click(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a mouse click action.
        
        Args:
            action: Dictionary containing action parameters
        
        Returns:
            Dictionary with action result
        """
        x = action["x"]
        y = action["y"]
        button = action.get("button", "left")
        clicks = action.get("clicks", 1)
        
        # Move mouse and click
        pyautogui.moveTo(x, y, duration=0.3)
        pyautogui.click(x=x, y=y, button=button, clicks=clicks)
        
        return {
            "action": "mouse_click",
            "position": {"x": x, "y": y},
            "button": button,
            "clicks": clicks,
            "status": "success"
        }
    
    async def _handle_keyboard_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a keyboard action.
        
        Args:
            action: Dictionary containing action parameters
        
        Returns:
            Dictionary with action result
        """
        action_type = action["action_type"]
        value = action["value"]
        
        if action_type.lower() == "type":
            pyautogui.write(value)
        elif action_type.lower() == "press":
            pyautogui.press(value)
        elif action_type.lower() == "hotkey":
            keys = [k.strip() for k in value.split('+')]
            pyautogui.hotkey(*keys)
        else:
            return {
                "action": "keyboard",
                "action_type": action_type,
                "value": value,
                "status": "error",
                "message": f"Unknown action type: {action_type}"
            }
        
        return {
            "action": "keyboard",
            "action_type": action_type,
            "value": value,
            "status": "success"
        }
    
    async def _handle_scroll_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a scroll action.
        
        Args:
            action: Dictionary containing action parameters
        
        Returns:
            Dictionary with action result
        """
        direction = action.get("direction", "down")
        amount = action.get("amount", 300)
        
        if direction.lower() in ["up", "down"]:
            scroll_amount = amount if direction.lower() == "up" else -amount
            pyautogui.scroll(scroll_amount)
        elif direction.lower() in ["left", "right"]:
            scroll_amount = -amount if direction.lower() == "left" else amount
            pyautogui.hscroll(scroll_amount)
        elif direction.lower() == "top":
            pyautogui.hotkey('home')
        elif direction.lower() == "bottom":
            pyautogui.hotkey('end')
        else:
            return {
                "action": "scroll",
                "direction": direction,
                "amount": amount,
                "status": "error",
                "message": f"Unknown scroll direction: {direction}"
            }
        
        return {
            "action": "scroll",
            "direction": direction,
            "amount": amount,
            "status": "success"
        }