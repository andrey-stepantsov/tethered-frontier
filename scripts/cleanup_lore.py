import os

def cleanup():
    # List of Title Case files to remove in favor of kebab-case versions
    files_to_remove = [
        "content/lore/The Bolas.md",
        "content/lore/The Breaker.md",
        "content/lore/The Strip.md",
        "content/lore/The Mirrors.md"
    ]

    print("Cleaning up redundant lore files...")
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Removed: {file_path}")
            except OSError as e:
                print(f"❌ Error removing {file_path}: {e}")
        else:
            print(f"⚠️  File not found (already removed?): {file_path}")

if __name__ == "__main__":
    cleanup()
