import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import requests

SETTINGS_FILE = "settings.json"

# Default templates
default_texts = {
    "Invalid Route": "Hi, your planned route seems to be invalid. Can you accept amended routing via {route}?",
    "Non-Standard Altitude": "Hi, your altitude is non-standard. I can offer you either {fl1} or {fl2}."
}

custom_texts = default_texts.copy()
formatted_routes = []  # Stores only route strings

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

def generate_message(event=None):
    mode = mode_var.get()

    if mode == "Invalid Route":
        selected = route_listbox.curselection()
        if selected:
            route = formatted_routes[selected[0]]
        else:
            route = entry1.get().strip()

        if not route:
            messagebox.showwarning("Missing input", "Please select a route or enter one manually.")
            return

        message = custom_texts["Invalid Route"].replace("{route}", route)

    elif mode == "Non-Standard Altitude":
        filed_fl = entry1.get().strip()
        if not filed_fl.isdigit():
            messagebox.showwarning("Invalid input", "Please enter a numeric flight level (e.g. 330).")
            return

        fl = int(filed_fl)
        fl1 = f"FL{fl - 10:03}"
        fl2 = f"FL{fl + 10:03}"

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
        label1.grid()
        entry1.grid()
        route_frame.grid()
        entry1.delete(0, tk.END)
        label1.config(text="Enter suggested routing (optional override):")
        alt_frame.grid_remove()

    elif mode == "Non-Standard Altitude":
        label1.config(text="Enter filed flight level (e.g. 330):")
        label1.grid()
        entry1.grid()
        alt_frame.grid()
        route_frame.grid_remove()
        entry1.delete(0, tk.END)

def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("420x260")

    info = ("Use placeholders:\n"
            "  {route} → suggested route\n"
            "  {fl1} and {fl2} → flight levels")
    ttk.Label(settings_window, text=info, foreground="gray").pack(anchor="w", padx=10, pady=(10, 0))

    ttk.Label(settings_window, text="Invalid Route Text:").pack(anchor="w", padx=10, pady=(10, 0))
    ir_entry = ttk.Entry(settings_window, width=70)
    ir_entry.insert(0, custom_texts["Invalid Route"])
    ir_entry.pack(padx=10, pady=5)

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

def fetch_routes():
    dept = dept_entry.get().strip().upper()
    dest = dest_entry.get().strip().upper()

    if not dept or not dest:
        messagebox.showwarning("Missing input", "Please enter both departure and destination ICAO codes.")
        return

    try:
        url = f"https://api.chrisgardiner.org/routes?dept={dept}&dest={dest}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print("API Response:", json.dumps(data, indent=2))

        routes = data.get("routes", [])
        route_listbox.delete(0, tk.END)
        formatted_routes.clear()

        if not routes:
            messagebox.showinfo("No Routes", f"No routes found for {dept} → {dest}.")
            return

        for r in routes:
            acft = r.get("acft", "Any")
            route_str = r.get("route", "").strip()

            # Format multi-line display
            first_line = f"{acft} |"
            second_line = f"{route_str}"
            display = f"{first_line}\n{second_line}" if route_str else "(No route)"
            route_listbox.insert(tk.END, display)
            formatted_routes.append(route_str)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch routes:\n{e}")

# --- UI ---
root = tk.Tk()
root.title("LazyATC")
root.geometry("600x600")
root.resizable(True, True)

root.bind("<Return>", generate_message)  # ENTER = Generate

# Menu
menubar = tk.Menu(root)
settings_menu = tk.Menu(menubar, tearoff=0)
settings_menu.add_command(label="Open Settings", command=open_settings)
menubar.add_cascade(label="Settings", menu=settings_menu)
root.config(menu=menubar)

mode_var = tk.StringVar()

frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)

# Mode buttons
button_frame = ttk.Frame(frame)
button_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10))
ttk.Label(button_frame, text="Select mode:").pack(side="left", padx=(0, 10))
ttk.Button(button_frame, text="Invalid Route", command=lambda: set_mode("Invalid Route")).pack(side="left")
ttk.Button(button_frame, text="Non-Standard Altitude", command=lambda: set_mode("Non-Standard Altitude")).pack(side="left")

# Shared label/input
label1 = ttk.Label(frame, text="")
label1.grid(row=1, column=0, sticky="w")
entry1 = ttk.Entry(frame)
entry1.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

# Route group
route_frame = ttk.Frame(frame)
route_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))

ttk.Label(route_frame, text="Departure (ICAO):").grid(row=0, column=0, sticky="w")
dept_entry = ttk.Entry(route_frame)
dept_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

ttk.Label(route_frame, text="Destination (ICAO):").grid(row=1, column=0, sticky="w")
dest_entry = ttk.Entry(route_frame)
dest_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

ttk.Button(route_frame, text="🔍 Get Routes", command=fetch_routes).grid(row=2, column=0, columnspan=2, pady=5)

ttk.Label(route_frame, text="Available Routes:").grid(row=3, column=0, sticky="nw")
route_listbox = tk.Listbox(route_frame, height=6)
route_listbox.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")

route_frame.columnconfigure(1, weight=1)

# Alt frame (not used, just keeps layout consistent)
alt_frame = ttk.Frame(frame)
alt_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

# Generate + Output
ttk.Button(frame, text="📋 Copy Message", command=generate_message).grid(row=9, column=0, columnspan=2, pady=10)

output_text = tk.Text(frame, height=4, wrap="word")
output_text.grid(row=10, column=0, columnspan=2, pady=5, sticky="nsew")

frame.columnconfigure(1, weight=1)
frame.rowconfigure(10, weight=1)
route_frame.rowconfigure(3, weight=1)

load_settings()
root.mainloop()
