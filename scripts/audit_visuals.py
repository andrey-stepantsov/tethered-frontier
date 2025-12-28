import os
import re

# Configuration
CONTENT_ROOT = "content"
CATEGORIES = ["", "characters", "locations", "lore"]
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
    """
    Scans a file for visual asset targets.
    Returns a list of (status, target_base_name) tuples.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Check if the file has the "NEVER display" comment block (global check)
    has_safety = "NEVER display the prompt text" in content

    # 2. Find all TARGETs
    matches = list(TARGET_PATTERN.finditer(content))
    
    # If no targets found
    if not matches:
        if not has_safety:
            return [("MISSING_BLOCK", None)]
        else:
            return [("MISSING_TARGET", None)]

    # If targets found, but safety text is missing entirely
    if not has_safety:
        return [("MISSING_BLOCK", None)]

    results = []
    for match in matches:
        target_name = match.group(1).strip()
        base_name, _ = os.path.splitext(target_name)
        
        found = False
        for ext in VALID_EXTENSIONS:
            if f"{base_name}{ext}" in existing_images:
                found = True
                break
        
        if found:
            results.append(("OK", base_name))
        else:
            results.append(("PENDING", base_name))
            
    return results

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
    duplicate_targets = []
    
    # Track seen targets to ensure uniqueness: {target_base_name: first_filename}
    seen_targets = {}
    
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
            file_results = check_file(filepath, existing_images)

            for status, target_base in file_results:
                if status in ["OK", "PENDING"]:
                    # Check for duplicates
                    if target_base in seen_targets:
                        original_file = seen_targets[target_base]
                        duplicate_targets.append((filename, target_base, original_file))
                        # Do not count as complete or pending if duplicate
                        continue
                    
                    seen_targets[target_base] = filename

                    if status == "OK":
                        complete += 1
                    elif status == "PENDING":
                        pending_generation.append((filename, target_base))
                
                elif status == "MISSING_TARGET":
                    missing_targets.append(filename)
                elif status == "MISSING_BLOCK":
                    missing_blocks.append(filename)

    # Report
    if duplicate_targets:
        print(f"\n[DUPLICATE TARGETS] ({len(duplicate_targets)})")
        print("Multiple files claim the same image target:")
        for fname, target, original in duplicate_targets:
            print(f"  - {fname} claims '{target}' (already claimed by {original})")

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
    print(f"TOTAL ACTIONABLE: {len(pending_generation) + len(missing_targets) + len(missing_blocks) + len(duplicate_targets)}")

if __name__ == "__main__":
    main()
