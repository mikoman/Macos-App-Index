import os
import subprocess
import datetime
import argparse

# Try to import tkinter for GUI selection
try:
    import tkinter as tk
    from tkinter import messagebox
    BULLET_AVAILABLE = False
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

def get_installed_apps():
    """
    Gets a list of installed applications from the /Applications and ~/Applications directories.
    """
    app_dirs = ["/Applications", os.path.expanduser("~/Applications")]
    apps = []
    for app_dir in app_dirs:
        if os.path.isdir(app_dir):
            for app in os.listdir(app_dir):
                if app.endswith(".app"):
                    apps.append(app.replace(".app", ""))
    return sorted(list(set(apps)))

def get_brew_packages():
    """
    Gets a list of installed Homebrew formulae.
    """
    try:
        result = subprocess.run(["brew", "list", "--formula"], capture_output=True, text=True, check=True)
        return result.stdout.strip().split("\n")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

def get_brew_casks():
    """
    Gets a list of installed Homebrew Casks.
    """
    try:
        result = subprocess.run(["brew", "list", "--cask"], capture_output=True, text=True, check=True)
        return result.stdout.strip().split("\n")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

def run_index_mode():
    """
    Scans the system and creates a file listing installed software.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"macos_installed_software_{now}.txt"

    installed_apps = get_installed_apps()
    brew_formulae = get_brew_packages()
    brew_casks = get_brew_casks()

    with open(filename, "w") as f:
        f.write("### macOS Installed Applications ###\n")
        if installed_apps:
            for app in installed_apps:
                f.write(f"{app}\n")
        else:
            f.write("No applications found in /Applications or ~/Applications.\n")

        f.write("\n### Homebrew Formulae ###\n")
        if brew_formulae:
            for formula in brew_formulae:
                f.write(f"{formula}\n")
        else:
            f.write("Homebrew not found or no formulae installed.\n")

        f.write("\n### Homebrew Casks ###\n")
        if brew_casks:
            for cask in brew_casks:
                f.write(f"{cask}\n")
        else:
            f.write("Homebrew not found or no casks installed.\n")

    print(f"Report saved to: {filename}")

def select_items_with_tkinter(title, items):
    """
    Use Tkinter to let the user select items from a list. Returns the selected items.
    If Tkinter is not available, returns the original list (select all).
    """
    if not TKINTER_AVAILABLE or not items:
        return items
    selected = []
    root = tk.Tk()
    root.title(title)
    root.geometry("600x500") # Increased width for columns
    tk.Label(root, text=title, font=("Arial", 14, "bold")).pack(pady=10)

    # Main frame to hold canvas and scrollbar
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Canvas for scrollable area
    canvas = tk.Canvas(main_frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Scrollbar
    scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Frame inside canvas to hold the checkboxes
    scrollable_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    scrollable_frame.bind("<Configure>", on_frame_configure)

    vars = []
    num_columns = 3
    for i, item in enumerate(items):
        var = tk.BooleanVar(value=True)
        chk = tk.Checkbutton(scrollable_frame, text=item, variable=var, anchor="w")
        row = i // num_columns
        col = i % num_columns
        chk.grid(row=row, column=col, sticky="w", padx=5, pady=2)
        vars.append((item, var))

    def on_ok():
        nonlocal selected
        selected = [item for item, var in vars if var.get()]
        root.destroy()
    ok_btn = tk.Button(root, text="OK", command=on_ok, width=10)
    ok_btn.pack(pady=10)
    root.mainloop()
    return selected

def run_restore_mode(filepath):
    """
    Restores software from a specified inventory file.
    """
    if not os.path.isfile(filepath):
        print(f"Error: File not found at '{filepath}'")
        return

    print(f"--- Parsing software list from {filepath} ---")
    apps = []
    formulae = []
    casks = []
    current_section = None

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("###"):
                if "macOS Installed Applications" in line:
                    current_section = 'apps'
                elif "Homebrew Formulae" in line:
                    current_section = 'formulae'
                elif "Homebrew Casks" in line:
                    current_section = 'casks'
                continue

            if current_section and not line.startswith("No ") and not line.startswith("Homebrew not found"):
                if current_section == 'apps':
                    apps.append(line)
                elif current_section == 'formulae':
                    formulae.append(line)
                elif current_section == 'casks':
                    casks.append(line)

    # Interactive selection for formulae and casks using Tkinter
    if TKINTER_AVAILABLE:
        if formulae:
            formulae = select_items_with_tkinter("Select Homebrew Formulae to install", formulae)
        if casks:
            casks = select_items_with_tkinter("Select Homebrew Casks to install", casks)
    else:
        if formulae or casks:
            print("\nNOTE: For interactive selection, Tkinter must be available (usually included with Python). Proceeding to install all items...\n")

    if formulae:
        print("\n--- Installing Homebrew Formulae ---")
        for formula in formulae:
            print(f"Installing brew formula '{formula}'...")
            try:
                subprocess.run(["brew", "install", formula], check=True)
            except subprocess.CalledProcessError as e:
                print(f"  > Failed to install '{formula}': {e}. Continuing...")
            except FileNotFoundError:
                print("  > ERROR: 'brew' command not found. Please install Homebrew first.")
                return
    
    if casks:
        print("\n--- Installing Homebrew Casks ---")
        for cask in casks:
            print(f"Installing brew cask '{cask}'...")
            try:
                subprocess.run(["brew", "install", "--cask", cask], check=True)
            except subprocess.CalledProcessError as e:
                print(f"  > Failed to install '{cask}': {e}. Continuing...")
            except FileNotFoundError:
                print("  > ERROR: 'brew' command not found. Please install Homebrew first.")
                return

    if apps:
        print("\n--- Manual Application Installation Required ---")
        print("The following applications cannot be installed automatically.")
        print("Please install them manually from the App Store or developer websites:")
        for app in apps:
            print(f"  - {app}")
            
    print("\n--- Restore process complete. ---")


def main():
    """
    Main function to parse arguments and run the script in the selected mode.
    """
    parser = argparse.ArgumentParser(
        description="A script to index and restore macOS applications and Homebrew packages.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--index',
        action='store_true',
        help='Scan the system and create the software list.\nThis is the default action if no arguments are provided.'
    )
    group.add_argument(
        '--restore',
        type=str,
        metavar='<filepath>',
        help='Parse the specified file and reinstall the software.'
    )

    args = parser.parse_args()

    if args.restore:
        run_restore_mode(args.restore)
    else:
        # Default to index mode if --index is specified or no arguments are given
        print("--- Running in Index Mode ---")
        run_index_mode()


if __name__ == "__main__":
    main()