# macOS Software Inventory & Restore Script

This Python script helps you create an inventory of installed macOS applications and Homebrew packages, and restore them on a new or clean system.

## Features

- **Index Mode**: Scans your Mac for installed applications and Homebrew packages, and saves the list to a timestamped file.
- **Restore Mode**: Reads a previously generated inventory file and reinstalls Homebrew formulae and casks. Lists applications that must be installed manually.
- **Interactive Restore GUI**: During restore, a graphical window (using Tkinter) lets you select which Homebrew formulae and casks to install with checkboxes.
- **Simple CLI**: Easy-to-use command-line interface with clear feedback and error handling.

## Requirements

- Python 3.x (Tkinter is included by default on macOS and most Python installations)
- Homebrew (for restore functionality)

## Usage

### 1. Index Mode (Default)

Scan your system and create a software inventory file:

```bash
python3 main.py
```

or explicitly:

```bash
python3 main.py --index
```

This will generate a file named like `macos_installed_software_YYYY-MM-DD_HH-MM-SS.txt` in the current directory.

### 2. Restore Mode

Restore Homebrew packages from a previously generated inventory file:

```bash
python3 main.py --restore <path_to_inventory_file>
```

- The script will attempt to reinstall all Homebrew formulae and casks listed in the file.
- You will be presented with a graphical window (Tkinter) to select which formulae and casks to install.
- It will print a list of regular applications for you to install manually (from the App Store or developer websites).

## Example

```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# No extra dependencies to install

# Create an inventory file
python3 main.py

# Restore from the generated file
python3 main.py --restore macos_installed_software_2024-06-07_15-30-00.txt
```

## Notes

- The script does **not** automatically install regular macOS applications (from /Applications or ~/Applications). You must install these manually.
- Homebrew must be installed and available in your PATH for the restore functionality to work.
- The script is safe to run multiple times; it will skip already installed Homebrew packages.
- If Tkinter is not available (very rare on macOS), the script will proceed to install all formulae and casks without interactive selection and will print a note.

## License

MIT License 
