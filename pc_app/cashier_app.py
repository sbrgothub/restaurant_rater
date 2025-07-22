# pc_app/cashier_app.py (FINAL CLOUD VERSION)
import tkinter as tk
from tkinter import messagebox
import pandas as pd
from sqlalchemy import create_engine, text
import os
import uuid
import qrcode
from PIL import Image, ImageTk
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- CONFIGURATION ---
# IMPORTANT: This MUST be the "External Database URL" from your Render.com PostgreSQL details page.
DATABASE_URL = "postgres://user:password@host:port/database" # <-- PASTE YOUR RENDER DATABASE URL HERE
# IMPORTANT: This MUST be the public URL of your web app hosted on Render.
PUBLIC_APP_URL = "https://my-restaurant-app.onrender.com" # <-- PASTE YOUR RENDER WEB APP URL HERE

engine = create_engine(DATABASE_URL)
last_processed_file = None

def process_csv(file_path):
    global last_processed_file
    if last_processed_file and os.path.exists(last_processed_file):
        try:
            os.remove(last_processed_file)
            print(f"Deleted previous bill: {last_processed_file}")
        except Exception as e:
            print(f"Could not delete previous file: {e}")
            
    try:
        df = pd.read_csv(file_path)
        with engine.connect() as conn:
            with conn.begin():
                unique_id = str(uuid.uuid4())[:8].upper()
                conn.execute(
                    text("INSERT INTO transactions (unique_id, status) VALUES (:uid, 'NEW')"),
                    {"uid": unique_id}
                )
                result = conn.execute(text("SELECT id FROM transactions WHERE unique_id = :uid"), {"uid": unique_id}).fetchone()
                transaction_id = result[0]

                for index, row in df.iterrows():
                    food_name = row['food_item']
                    quantity = int(row['quantity'])
                    
                    conn.execute(
                        text("INSERT INTO transaction_items (transaction_id, food_name) VALUES (:tid, :fname)"),
                        {"tid": transaction_id, "fname": food_name}
                    )
                    
                    # Check if food exists before updating or inserting
                    food_exists = conn.execute(text("SELECT id FROM foods WHERE name = :fname"), {"fname": food_name}).fetchone()
                    if food_exists:
                        conn.execute(
                            text("UPDATE foods SET total_quantity = total_quantity + :qty WHERE name = :fname"),
                            {"qty": quantity, "fname": food_name}
                        )
                    else:
                        conn.execute(
                            text("INSERT INTO foods (name, total_quantity) VALUES (:fname, :qty)"),
                            {"fname": food_name, "qty": quantity}
                        )
        
        full_url = f"{PUBLIC_APP_URL}/rate/{unique_id}"
        root.after(0, update_gui_with_qr, full_url, unique_id)
        last_processed_file = file_path

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        messagebox.showerror("Processing Error", f"Could not process the new bill:\n{e}")

def update_gui_with_qr(url, unique_id):
    """Safely updates the Tkinter GUI from a background thread."""
    print(f"Updating GUI with QR for URL: {url}")
    qr_img = qrcode.make(url)
    tk_img = ImageTk.PhotoImage(qr_img)
    qr_code_label.config(image=tk_img)
    qr_code_label.image = tk_img
    id_label.config(text=f"ID: {unique_id}")
    info_label.config(text="Scan the QR Code to Rate Your Meal")

# --- WATCHDOG FOLDER MONITORING CLASS ---
class CSVHandler(FileSystemEventHandler):
    """A handler for file system events."""
    def on_created(self, event):
        """Called when a file or directory is created."""
        # Check if the created event is for a CSV file and not a directory
        if not event.is_directory and event.src_path.endswith('.csv'):
            print(f"Watchdog detected new CSV file: {event.src_path}")
            # Wait a brief moment to ensure the file is fully written by the POS system
            time.sleep(0.5) 
            # Process the detected file
            process_csv(event.src_path)

# --- GUI Setup ---
root = tk.Tk()
root.title("Restaurant Rating QR Display (Auto-Mode)")
root.geometry("450x550")
main_frame = tk.Frame(root, padx=20, pady=20)
main_frame.pack(expand=True)
info_label = tk.Label(root, text="Waiting for new bill from POS system...", font=("Helvetica", 16, "bold"), fg="#333")
info_label.pack(pady=20)
qr_code_label = tk.Label(main_frame)
qr_code_label.pack(pady=10)
id_label = tk.Label(main_frame, text="", font=("Helvetica", 12), fg="#555")
id_label.pack(pady=5)

# --- START THE FOLDER WATCHER ---
if __name__ == "__main__":
    # The path to watch is the folder where this script is located
    path_to_watch = os.path.dirname(os.path.abspath(__file__))
    
    event_handler = CSVHandler()
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=False)
    
    # Run the observer in a separate (daemon) thread so it doesn't block the GUI
    observer_thread = threading.Thread(target=observer.start, daemon=True)
    observer_thread.start()
    
    print(f"--- Monitoring for new CSV files in: {path_to_watch} ---")
    
    # Start the Tkinter GUI main loop
    root.mainloop()

    # Cleanly stop the observer when the GUI window is closed
    observer.stop()
    observer.join()
    print("--- Monitoring stopped. ---")