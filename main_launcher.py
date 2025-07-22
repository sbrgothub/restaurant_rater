# main_launcher.py (BATCH FILE VERSION)
import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

def get_path(relative_path):
    """ Gets the absolute path to a resource, for both dev and PyInstaller. """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def start_system():
    """Runs the start_system.bat file."""
    try:
        # Use CREATE_NO_WINDOW to run the batch file invisibly
        subprocess.Popen([get_path('start_system.bat')], creationflags=subprocess.CREATE_NO_WINDOW)
        start_btn.config(state="disabled")
        stop_btn.config(state="normal")
        status_label.config(text="Status: All Systems Running", fg="green")
    except Exception as e:
        messagebox.showerror("Error", f"Could not execute start_system.bat: {e}")

def stop_system():
    """Runs the stop_system.bat file."""
    try:
        subprocess.Popen([get_path('stop_system.bat')], creationflags=subprocess.CREATE_NO_WINDOW)
        start_btn.config(state="normal")
        stop_btn.config(state="disabled")
        status_label.config(text="Status: Stopped", fg="red")
    except Exception as e:
        messagebox.showerror("Error", f"Could not execute stop_system.bat: {e}")

def on_closing():
    if messagebox.askokcancel("Quit", "This will stop all running processes. Are you sure?"):
        stop_system()
        root.destroy()

# --- GUI Setup ---
root = tk.Tk()
root.title("Restaurant System Control Panel")
# ... (rest of the GUI code is the same)
root.geometry("400x200")
main_frame = tk.Frame(root, padx=20, pady=20)
main_frame.pack(expand=True)
status_label = tk.Label(main_frame, text="Status: Stopped", font=("Helvetica", 14, "bold"), fg="red")
status_label.pack(pady=10)
start_btn = tk.Button(main_frame, text="Start System", command=start_system, font=("Helvetica", 12), bg="#4CAF50", fg="white", width=15)
start_btn.pack(pady=5)
stop_btn = tk.Button(main_frame, text="Stop System", command=stop_system, font=("Helvetica", 12), bg="#f44336", fg="white", width=15, state="disabled")
stop_btn.pack(pady=5)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()