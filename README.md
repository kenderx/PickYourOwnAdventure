# Pick-Your-Own-Adventure Game Engine

A data-driven, highly immersive Windows desktop application for playing interactive pick-your-own-adventure stories. Built with Python, CustomTkinter, and pygame.

---

## Features

- **Rich Visuals**: Powered by a custom theme engine (supporting Dark, Light, and Sepia modes).
- **Immersive Typography**: Uses clean serif typography for stories (`Georgia`) and system UI fonts (`Segoe UI`) for interfaces.
- **Dynamic Story Elements**: Handles typewriter text animations, custom character sheets, condition gating (requirements/unless), and story effects.
- **Audio Experience**: Crossfaded ambient music and action sound effects per node/choice.
- **Saves System**: 3 slots for progress save/load.
- **Data Driven**: Stories are fully written in human-readable YAML configs.

---

## Getting Started

### Prerequisites

1. **Python 3.11+**:
   If Python is not installed, install it using `winget` (run PowerShell as Administrator):
   ```powershell
   winget install Python.Python.3.11 --scope user --silent --accept-package-agreements --accept-source-agreements --override "/quiet InstallAllUsers=0 PrependPath=1 Include_launcher=0"
   ```

2. **Dependencies**:
   Install all required libraries using `pip`:
   ```cmd
   pip install -r requirements.txt
   ```

---

## Running the Application

To start the game launcher and play:
```cmd
python main.py
```

---

## Authoring Custom Stories

Stories are written in YAML and loaded dynamically. For a complete guide on variables, conditions, choices, effects, and assets, see [stories/README.md](stories/README.md).

---

## Packaging into a Single `.exe` File

The application can be packaged into a standalone Windows executable.

1. **Build command**:
   Run PyInstaller with the provided build specification file:
   ```cmd
   pyinstaller --clean build.spec
   ```
2. **Result**:
   The standalone executable `PickYourOwnAdventure.exe` will be generated inside the `dist/` directory. All themes, story data, and cover art are embedded directly into the executable file!
