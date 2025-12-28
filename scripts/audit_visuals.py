import os
import re

# Configuration
CONTENT_ROOT = "content"
CATEGORIES = ["characters", "locations", "lore"]
VALID_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

# Regex to find the TARGET line inside the HTML comment
# Matches: TARGET: filename (with optional whitespace)
TARGET_PATTERN = re.compile(r'TARGET:\s*([\w\-\.]+)', re.IGNORECASE)

def get_all_images(root_dir):
    """Builds a set of all existing image filenames (without path) for fast lookup."""
    images = set()
    for root, _, files in os.walk(root_dir):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() in VALID_EXTENSIONS:
                images.add(file)
    return images

def check_file(filepath, existing_images):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Check if the file has the "NEVER display" comment block
    if "NEVER display the prompt text" not in content:
        return "MISSING_BLOCK", None

    # 2. Extract the TARGET filename
    match = TARGET_PATTERN.search(content)
    if not match:
        return "MISSING_TARGET", None

    target_name = match.group(1).strip()
    
    # Strip extension if the user included it in the target (e.g. "vance.png" -> "vance")
    base_name, _ = os.path.splitext(target_name)

    # 3. Check if any image with this base name exists
    found = False
    for ext in VALID_EXTENSIONS:
        if f"{base_name}{ext}" in existing_images:
            found = True
            break
            
    if found:
        return "OK", target_name
    else:
        return "PENDING", target_name

def main():
    print(f"--- VISUAL ASSET AUDIT ---")
    
    # Index all images first
    print(f"Indexing images in {CONTENT_ROOT}...")
    existing_images = get_all_images(CONTENT_ROOT)
    print(f"Found {len(existing_images)} images.")
    print("-" * 30)

    missing_blocks = []
    missing_targets = []
    pending_generation = []
    complete = 0

    # Scan content files
    for category in CATEGORIES:
        dir_path = os.path.join(CONTENT_ROOT, category)
        if not os.path.exists(dir_path):
            continue

        for filename in os.listdir(dir_path):
            if not filename.endswith(".md"):
                continue

            filepath = os.path.join(dir_path, filename)
            status, target = check_file(filepath, existing_images)

            if status == "OK":
                complete += 1
            elif status == "PENDING":
                pending_generation.append((filename, target))
            elif status == "MISSING_TARGET":
                missing_targets.append(filename)
            elif status == "MISSING_BLOCK":
                missing_blocks.append(filename)

    # Report
    if pending_generation:
        print(f"\n[PENDING GENERATION] ({len(pending_generation)})")
        print("Prompts exist, but images are missing:")
        for fname, target in pending_generation:
            print(f"  - {fname} (Target: {target}.*)")

    if missing_targets:
        print(f"\n[MISSING TARGET] ({len(missing_targets)})")
        print("Comment block exists, but 'TARGET:' line is missing:")
        for fname in missing_targets:
            print(f"  - {fname}")

    if missing_blocks:
        print(f"\n[MISSING PROMPT BLOCK] ({len(missing_blocks)})")
        print("No visual prompt block found:")
        for fname in missing_blocks:
            print(f"  - {fname}")

    print("-" * 30)
    print(f"TOTAL COMPLETE: {complete}")
    print(f"TOTAL ACTIONABLE: {len(pending_generation) + len(missing_targets) + len(missing_blocks)}")

if __name__ == "__main__":
    main()
