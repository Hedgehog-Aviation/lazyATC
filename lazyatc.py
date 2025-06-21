import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

SETTINGS_FILE = "settings.json"

# Default templates
default_texts = {
    "Invalid Route": "Hi, your planned route seems to be invalid. Can you accept amended routing via {route}?",
    "Non-Standard Altitude": "Hi, your altitude is non-standard. I can offer you either {fl1} or {fl2}."
}

custom_texts = default_texts.copy()

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                custom_texts.update(data)
        except Exception as e:
            messagebox.showwarning("Settings Error", f"Could not load settings: {e}")

def save_settings_to_file():
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(custom_texts, f, indent=2)
    except Exception as e:
        messagebox.showerror("Save Error", f"Could not save settings: {e}")

def set_mode(new_mode):
    mode_var.set(new_mode)
    update_inputs()

def generate_message():
    mode = mode_var.get()
    if mode == "Invalid Route":
        route = entry1.get().strip()
        if not route:
            messagebox.showwarning("Missing input", "Please enter the suggested routing.")
            return
        message = custom_texts["Invalid Route"].replace("{route}", route)
    elif mode == "Non-Standard Altitude":
        fl1 = entry1.get().strip()
        fl2 = entry2.get().strip()
        if not fl1 or not fl2:
            messagebox.showwarning("Missing input", "Please enter both flight levels.")
            return
        message = custom_texts["Non-Standard Altitude"].replace("{fl1}", fl1).replace("{fl2}", fl2)
    else:
        messagebox.showwarning("Mode not selected", "Please select a mode.")
        return

    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, message)
    root.clipboard_clear()
    root.clipboard_append(message)

def update_inputs():
    mode = mode_var.get()
    if mode == "Invalid Route":
        label1.config(text="Enter suggested routing:")
        label2.grid_remove()
        entry2.grid_remove()
    elif mode == "Non-Standard Altitude":
        label1.config(text="Enter first flight level:")
        label2.config(text="Enter second flight level:")
        label2.grid(row=2, column=0, sticky="w", padx=5)
        entry2.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("420x260")

    # Instructions
    info = ("Use placeholders:\n"
            "  {route} → suggested route\n"
            "  {fl1} and {fl2} → flight levels")
    ttk.Label(settings_window, text=info, foreground="gray").pack(anchor="w", padx=10, pady=(10, 0))

    # Invalid Route template
    ttk.Label(settings_window, text="Invalid Route Text:").pack(anchor="w", padx=10, pady=(10, 0))
    ir_entry = ttk.Entry(settings_window, width=70)
    ir_entry.insert(0, custom_texts["Invalid Route"])
    ir_entry.pack(padx=10, pady=5)

    # Non-Standard Altitude template
    ttk.Label(settings_window, text="Non-Standard Altitude Text:").pack(anchor="w", padx=10, pady=(10, 0))
    alt_entry = ttk.Entry(settings_window, width=70)
    alt_entry.insert(0, custom_texts["Non-Standard Altitude"])
    alt_entry.pack(padx=10, pady=5)

    def save_settings():
        custom_texts["Invalid Route"] = ir_entry.get()
        custom_texts["Non-Standard Altitude"] = alt_entry.get()
        save_settings_to_file()
        settings_window.destroy()

    ttk.Button(settings_window, text="Save", command=save_settings).pack(pady=10)

# --- Main UI ---
root = tk.Tk()
root.title("DEL Assistant")
root.geometry("400x300")
root.resizable(False, False)

# Menu bar
menubar = tk.Menu(root)
settings_menu = tk.Menu(menubar, tearoff=0)
settings_menu.add_command(label="Open Settings", command=open_settings)
menubar.add_cascade(label="Settings", menu=settings_menu)
root.config(menu=menubar)

mode_var = tk.StringVar()

frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)

button_frame = ttk.Frame(frame)
button_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10))
ttk.Label(button_frame, text="Select mode:").pack(side="left", padx=(0, 10))
ttk.Button(button_frame, text="Invalid Route", command=lambda: set_mode("Invalid Route")).pack(side="left")
ttk.Button(button_frame, text="Non-Standard Altitude", command=lambda: set_mode("Non-Standard Altitude")).pack(side="left")

label1 = ttk.Label(frame, text="")
label1.grid(row=1, column=0, sticky="w")
entry1 = ttk.Entry(frame)
entry1.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

label2 = ttk.Label(frame, text="")
entry2 = ttk.Entry(frame)

button = ttk.Button(frame, text="📋 Copy Message", command=generate_message)
button.grid(row=3, column=0, columnspan=2, pady=10)

output_text = tk.Text(frame, height=3, wrap="word")
output_text.grid(row=4, column=0, columnspan=2, pady=5, sticky="nsew")

frame.columnconfigure(1, weight=1)

load_settings()
root.mainloop()
