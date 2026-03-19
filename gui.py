"""Egyptian Horoscope — Desktop GUI

Run directly:   python gui.py
Build exe:      see build_windows.bat
"""

from __future__ import annotations

import os
import sys
import threading
from datetime import date
from pathlib import Path

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# ── resolve base directory whether running as .py or PyInstaller bundle ──────
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

# Load .env from the same folder as the script / exe
from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

from app.systems.egyptian import get_egyptian_sign
from app.ai.generator import generate_daily_reading


# ── API key prompt ────────────────────────────────────────────────────────────

def _require_api_key(root: tk.Tk) -> None:
    """If ANTHROPIC_API_KEY is absent, show a one-time entry dialog and save it."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return

    dialog = tk.Toplevel(root)
    dialog.title("API Key Required")
    dialog.resizable(False, False)
    dialog.grab_set()

    ttk.Label(dialog, text="Enter your Anthropic API Key:").pack(padx=24, pady=(18, 6))
    key_var = tk.StringVar()
    entry = ttk.Entry(dialog, textvariable=key_var, width=52, show="*")
    entry.pack(padx=24, pady=(0, 12))
    entry.focus_set()

    def save() -> None:
        key = key_var.get().strip()
        if not key:
            messagebox.showwarning("Missing Key", "Please enter an API key.", parent=dialog)
            return
        os.environ["ANTHROPIC_API_KEY"] = key
        env_path = BASE_DIR / ".env"
        env_path.write_text(f"ANTHROPIC_API_KEY={key}\n", encoding="utf-8")
        dialog.destroy()

    ttk.Button(dialog, text="Save & Continue", command=save).pack(pady=(0, 18))
    dialog.bind("<Return>", lambda _: save())
    root.wait_window(dialog)


# ── main GUI ──────────────────────────────────────────────────────────────────

def main() -> None:
    root = tk.Tk()
    root.title("Egyptian Horoscope")
    root.resizable(False, False)

    _require_api_key(root)

    # ── input section ─────────────────────────────────────────────────────────
    form = ttk.Frame(root, padding=16)
    form.grid(row=0, column=0, sticky="ew")

    ttk.Label(form, text="Name").grid(row=0, column=0, sticky="w")
    name_var = tk.StringVar()
    ttk.Entry(form, textvariable=name_var, width=36).grid(
        row=0, column=1, sticky="ew", padx=(10, 0), pady=4
    )

    ttk.Label(form, text="Birth Date").grid(row=1, column=0, sticky="w")
    date_var = tk.StringVar()
    ttk.Entry(form, textvariable=date_var, width=36).grid(
        row=1, column=1, sticky="ew", padx=(10, 0), pady=4
    )
    ttk.Label(form, text="YYYY-MM-DD", foreground="gray").grid(
        row=2, column=1, sticky="w", padx=(10, 0)
    )

    btn = ttk.Button(form, text="Get Reading")
    btn.grid(row=3, column=0, columnspan=2, pady=(14, 0))

    # ── output section ────────────────────────────────────────────────────────
    out = scrolledtext.ScrolledText(
        root, width=64, height=22, wrap=tk.WORD,
        state="disabled", padx=10, pady=10, font=("Segoe UI", 10)
    )
    out.grid(row=1, column=0, padx=16, pady=(8, 16), sticky="nsew")

    # ── logic ─────────────────────────────────────────────────────────────────
    def set_output(text: str) -> None:
        out.configure(state="normal")
        out.delete("1.0", tk.END)
        out.insert(tk.END, text)
        out.configure(state="disabled")

    def on_click() -> None:
        name = name_var.get().strip()
        dob = date_var.get().strip()

        if not name or not dob:
            messagebox.showwarning("Missing Input", "Please enter both a name and a birth date.")
            return

        try:
            birth = date.fromisoformat(dob)
        except ValueError:
            messagebox.showerror("Invalid Date", "Birth date must be in YYYY-MM-DD format.\nExample: 1990-06-15")
            return

        btn.configure(state="disabled")
        set_output("Consulting the stars…")

        def worker() -> None:
            try:
                chart = get_egyptian_sign(birth.month, birth.day)
                reading = generate_daily_reading("egyptian", chart, name, date.today())
                traits = ", ".join(chart["traits"])
                result = (
                    f"Sign:    {chart['sign']}  ·  {chart['deity']}\n"
                    f"Animal:  {chart['sacred_animal']}\n"
                    f"Element: {chart['element']}  ·  {chart['quality']}\n"
                    f"Traits:  {traits}\n"
                    f"{'─' * 52}\n\n"
                    f"{reading}"
                )
            except Exception as exc:
                result = f"Something went wrong:\n\n{exc}"

            root.after(0, lambda: (set_output(result), btn.configure(state="normal")))

        threading.Thread(target=worker, daemon=True).start()

    btn.configure(command=on_click)
    root.bind("<Return>", lambda _: on_click())

    root.mainloop()


if __name__ == "__main__":
    main()
