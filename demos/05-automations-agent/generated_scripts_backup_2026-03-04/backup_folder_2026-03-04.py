"""
Backs up all files (including nested) in a source folder to a new backup
directory, renaming each file with the current date (YYYY-MM-DD) appended.

Usage:
    python backup_folder.py <source_folder> [--dest <destination_folder>]

If no source is provided, a demo runs using a temporary folder.
"""

import os
import shutil
import argparse
import tempfile
from datetime import date


def backup_folder(source_folder, dest_folder=None):
    today = date.today().strftime("%Y-%m-%d")
    source_folder = os.path.abspath(source_folder)

    if not os.path.isdir(source_folder):
        print(f"❌ Error: '{source_folder}' is not a valid directory.")
        return 0

    if dest_folder is None:
        parent = os.path.dirname(source_folder)
        folder_name = os.path.basename(source_folder)
        dest_folder = os.path.join(parent, f"{folder_name}_backup_{today}")

    dest_folder = os.path.abspath(dest_folder)

    print(f"📁 Source : {source_folder}")
    print(f"💾 Backup : {dest_folder}")
    print(f"📅 Date   : {today}")
    print("-" * 60)

    files_copied = 0

    for root, dirs, files in os.walk(source_folder):
        rel_path = os.path.relpath(root, source_folder)
        dest_dir = os.path.join(dest_folder, rel_path) if rel_path != "." else dest_folder
        os.makedirs(dest_dir, exist_ok=True)

        for filename in files:
            name, ext = os.path.splitext(filename)
            new_filename = f"{name}_{today}{ext}"

            src_file = os.path.join(root, filename)
            dest_file = os.path.join(dest_dir, new_filename)

            shutil.copy2(src_file, dest_file)

            display_src = os.path.join(rel_path, filename) if rel_path != "." else filename
            print(f"  ✅  {display_src}")
            print(f"       → {os.path.join(rel_path, new_filename) if rel_path != '.' else new_filename}")
            files_copied += 1

    print("-" * 60)
    print(f"🎉 Done! {files_copied} file(s) backed up to:\n   {dest_folder}")
    return files_copied


def run_demo():
    """Creates a temporary folder structure and runs a demo backup."""
    print("🔧 No source folder provided — running DEMO mode...\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Build a sample folder structure
        sample_files = [
            "report.txt",
            "notes.md",
            "images/photo.png",
            "images/banner.jpg",
            "docs/summary.docx",
            "docs/archive/old_notes.txt",
        ]

        for rel_path in sample_files:
            full_path = os.path.join(tmpdir, "my_project", rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(f"Sample content for {rel_path}\n")

        source = os.path.join(tmpdir, "my_project")
        dest   = os.path.join(tmpdir, "my_project_backup")

        backup_folder(source, dest)

        # Show the resulting backup tree
        print("\n📂 Backup directory structure:")
        for root, dirs, files in os.walk(dest):
            level = root.replace(dest, "").count(os.sep)
            indent = "  " * level
            print(f"{indent}📁 {os.path.basename(root)}/")
            for f in files:
                print(f"{indent}  📄 {f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Backup a folder's files with today's date appended to each filename."
    )
    parser.add_argument(
        "source", nargs="?", default=None,
        help="Path to the folder you want to back up."
    )
    parser.add_argument(
        "--dest", default=None,
        help="(Optional) Custom path for the backup folder."
    )
    args = parser.parse_args()

    if args.source:
        backup_folder(args.source, args.dest)
    else:
        run_demo()
