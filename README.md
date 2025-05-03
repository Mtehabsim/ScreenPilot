# ScreenPilot

MCP server to let LLM take full control on your device by providing screen automation toolkit for controlling and interacting with graphical user interfaces. Good for automation, education and having fun.


## Main Features

- 📷 Screen capture and analysis
- 🖱️ Mouse control (clicking, positioning)
- ⌨️ Keyboard input (typing, key presses, hotkeys)

## watch demo
<video width="320" height="240" controls>
  <source src="Screen%20Pilot.mp4" type="video/mp4">
</video>

## Installation
0. Install python 3.12
1. Clone the repository:
   ```bash
   git clone https://github.com/Mtehabsim/ScreenPilot.git
   ```
2. create virtiual environment
```bash

python -m venv venv
```
3. activate the env
```bash
venv\Scripts\activate
```
4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Open Claude AI desktop
6. file -> settings -> developer -> edit config
7. open config file and paste this
```bash
{
    "mcpServers": {
        "device-controll": {
            "command": "pathToEnv\\venv\\Scripts\\python.exe",
            "args": [
                "pathToProject\\ScreenPilot\\main.py"
            ]
        }
    }
}

```
8. Replace
    "pathToEnv\\venv\\Scripts\\python.exe" → with the full path to your python.exe
    "pathToProject\\ScreenPilot\\main.py" → with the full path to your main.py file

9. Save the config file.

10. Open Claude AI Desktop.

11. Go to File → Exit

12. You can now open Claude AI Desktop and enjoy ScreenPilot.


### Available Tools

- **Screen Capture**: Take screenshots and get screen information
- **Mouse Control**: Move the mouse and perform clicks
- **Keyboard Actions**: Type text, press keys, and use hotkey combinations
- **Scrolling**: Scroll in different directions and to specific positions
- **Element Detection**: Check if elements exist on screen and wait for them to appear
- **Action Sequences**: Perform multiple actions in sequence

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

