"""
Copies all .py files in the current directory into a new date-stamped folder,
renaming each file to include the current date as a prefix (YYYY-MM-DD_filename.py).
"""

import os
import shutil
from datetime import date


def archive_python_files():
    today = date.today().strftime("%Y-%m-%d")
    output_folder = today

    # Create the output folder
    os.makedirs(output_folder, exist_ok=True)
    print(f"📁 Folder created: '{output_folder}/'")

    # Find all .py files in the current directory (not inside subfolders)
    py_files = [
        f for f in os.listdir(".")
        if f.endswith(".py") and os.path.isfile(f)
    ]

    if not py_files:
        print("⚠️  No .py files found in the current directory.")
        return

    copied = 0
    for filename in py_files:
        new_name = f"{today}_{filename}"
        dest = os.path.join(output_folder, new_name)
        shutil.copy2(filename, dest)
        print(f"  ✅ {filename}  →  {output_folder}/{new_name}")
        copied += 1

    print(f"\n🎉 Done! {copied} file(s) copied into '{output_folder}/'.")


if __name__ == "__main__":
    archive_python_files()
