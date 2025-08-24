#!/usr/bin/env python3
"""Demo script for Instagram Helper GUI."""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def show_gui_demo():
    """Show a demo of the GUI without running the actual scraper."""

    root = tk.Tk()
    root.title("Instagram Helper - Demo Mode")
    root.geometry("800x600")

    # Main frame
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Title
    title_label = ttk.Label(main_frame, text="Instagram Helper GUI Demo", font=("Arial", 18, "bold"))
    title_label.pack(pady=(0, 20))

    # Demo info
    info_text = """
This is a demo of the Instagram Helper GUI interface.

Features demonstrated:
• Real-time log monitoring
• Configurable Instagram accounts
• Adjustable settings (max post age, posts per account, timeout)
• Progress tracking with visual progress bar
• Start/stop controls
• Live status updates

The actual GUI application includes:
• Full Instagram scraping functionality
• Browser automation with Playwright
• HTML report generation
• Multi-threaded operation for responsive UI

To run the full application:
    python gui_app.py
    or
    python run_gui.py
"""

    info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT, font=("Arial", 10))
    info_label.pack(pady=(0, 20))

    # Demo controls
    control_frame = ttk.LabelFrame(main_frame, text="Demo Controls", padding="15")
    control_frame.pack(fill=tk.X, pady=(0, 20))

    # Settings demo
    settings_frame = ttk.Frame(control_frame)
    settings_frame.pack(fill=tk.X)

    ttk.Label(settings_frame, text="Max Post Age (days):").grid(row=0, column=0, sticky="w", padx=(0, 10))
    max_age_var = tk.StringVar(value="7")
    max_age_entry = ttk.Entry(settings_frame, textvariable=max_age_var, width=10)
    max_age_entry.grid(row=0, column=1, padx=(0, 20))

    ttk.Label(settings_frame, text="Max Posts per Account:").grid(row=0, column=2, sticky="w", padx=(0, 10))
    max_posts_var = tk.StringVar(value="5")
    max_posts_entry = ttk.Entry(settings_frame, textvariable=max_posts_var, width=10)
    max_posts_entry.grid(row=0, column=3)

    # Account demo
    account_frame = ttk.LabelFrame(main_frame, text="Sample Instagram Accounts", padding="15")
    account_frame.pack(fill=tk.X, pady=(0, 20))

    account_listbox = tk.Listbox(account_frame, height=6)
    sample_accounts = ["gijon", "aytoviedo", "cultura.gijon", "centroniemeyer", "museosgijonxixon"]
    for account in sample_accounts:
        account_listbox.insert(tk.END, account)

    account_listbox.pack(fill=tk.X)

    # Demo buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=20)

    def show_settings():
        messagebox.showinfo("Current Settings",
                          f"Max Post Age: {max_age_var.get()} days\n"
                          f"Max Posts per Account: {max_posts_var.get()}")

    def show_accounts():
        selection = account_listbox.curselection()
        if selection:
            selected = [account_listbox.get(i) for i in selection]
            messagebox.showinfo("Selected Accounts", f"Selected: {', '.join(selected)}")
        else:
            messagebox.showinfo("Selected Accounts", "No accounts selected")

    def launch_full_gui():
        if messagebox.askyesno("Launch Full GUI",
                              "Would you like to launch the full Instagram Helper GUI?"):
            root.destroy()
            try:
                from gui_app import main
                main()
            except ImportError as e:
                messagebox.showerror("Error", f"Could not launch full GUI: {e}")

    ttk.Button(button_frame, text="Show Current Settings", command=show_settings).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(button_frame, text="Show Selected Accounts", command=show_accounts).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(button_frame, text="Launch Full GUI", command=launch_full_gui).pack(side=tk.LEFT)

    # Status
    status_label = ttk.Label(main_frame, text="Demo Mode - No actual scraping will occur",
                            font=("Arial", 9), foreground="gray")
    status_label.pack(side=tk.BOTTOM, pady=(20, 0))

    root.mainloop()

if __name__ == "__main__":
    show_gui_demo()
