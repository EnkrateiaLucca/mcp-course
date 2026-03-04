"""
Explores the current (or given) folder: lists files with sizes,
counts by extension, and shows total disk usage.
"""

import os
import sys
from collections import defaultdict


def format_size(size_bytes):
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def explore_folder(path="."):
    print(f"\n📁 Exploring: {os.path.abspath(path)}")
    print("=" * 50)

    ext_counts = defaultdict(int)
    ext_sizes  = defaultdict(int)
    total_size = 0
    total_files = 0
    entries = []

    for name in sorted(os.listdir(path)):
        full = os.path.join(path, name)
        is_dir = os.path.isdir(full)
        try:
            size = os.path.getsize(full)
        except OSError:
            size = 0

        entries.append((name, is_dir, size))

        if not is_dir:
            total_files += 1
            total_size  += size
            ext = os.path.splitext(name)[1].lower() or "(no ext)"
            ext_counts[ext] += 1
            ext_sizes[ext]  += size

    # Print directory listing
    for name, is_dir, size in entries:
        icon = "📂" if is_dir else "📄"
        label = "<DIR>" if is_dir else format_size(size)
        print(f"  {icon}  {name:<35} {label}")

    # Summary
    print("\n" + "-" * 50)
    print(f"  Total files : {total_files}")
    print(f"  Total size  : {format_size(total_size)}")

    if ext_counts:
        print("\n  By extension:")
        for ext, count in sorted(ext_counts.items(), key=lambda x: -x[1]):
            print(f"    {ext:<15} {count:>3} file(s)   {format_size(ext_sizes[ext])}")

    print()


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    explore_folder(folder)
