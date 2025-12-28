import os
import re
import sys

# CONFIGURATION
CONTENT_DIR = "content"
ASSETS_DIR = os.path.join(CONTENT_DIR, "assets", "images")
MARKER = "NEVER display the prompt text to the reader."
SUPPORTED_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp"]

def get_target_basename(content, filename):
    """
    Determines the intended base filename (without extension).
    Priority 1: 'TARGET: filename' inside comments.
    Priority 2: Derive from markdown filename.
    """
    # Check for explicit TARGET:
    target_match = re.search(r"TARGET:\s*([\w\-\.]+)", content, re.IGNORECASE)
    if target_match:
        name = target_match.group(1).strip()
        return os.path.splitext(name)[0]

    # Fallback to markdown filename
    return os.path.splitext(filename)[0]

def find_existing_image(basename):
    """
    Checks if an image with the given basename exists in ASSETS_DIR
    with any supported extension. Returns the full filename if found.
    """
    for ext in SUPPORTED_EXTENSIONS:
        candidate = basename + ext
        if os.path.exists(os.path.join(ASSETS_DIR, candidate)):
            return candidate
    return None

def has_image_link(content):
    """
    Checks if the content already contains a wikilink to an image.
    Matches ![[...]]
    """
    return re.search(r"!\[\[.*?\]\]", content) is not None

def inject_link(filepath, image_filename):
    """
    Inserts the image link after the YAML frontmatter.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    frontmatter_count = 0
    insert_index = 0
    has_frontmatter = False

    # Find the end of the frontmatter (second '---')
    for i, line in enumerate(lines):
        if line.strip() == "---":
            frontmatter_count += 1
            if frontmatter_count == 2:
                insert_index = i + 1
                has_frontmatter = True
                break
    
    # If no frontmatter found (rare), insert at top
    if not has_frontmatter:
        insert_index = 0

    # Construct the link
    # We add a newline before and after to ensure separation
    link_line = f"\n![[{image_filename}]]\n"
    
    lines.insert(insert_index, link_line)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)

def main(dry_run=False):
    print(f"[-] Scanning '{CONTENT_DIR}' for unlinked visuals...")
    if dry_run:
        print("[-] Mode: DRY RUN (No files will be modified)")

    linked_count = 0

    for root, _, files in os.walk(CONTENT_DIR):
        for file in files:
            if not file.endswith(".md"):
                continue

            filepath = os.path.join(root, file)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Only process files that have a prompt marker
            if MARKER not in content:
                continue

            # Check if link already exists
            if has_image_link(content):
                continue

            basename = get_target_basename(content, file)

            # Find the actual image file
            image_filename = find_existing_image(basename)
            
            if not image_filename:
                print(f"[!] Image missing for: {file} (Expected base: {basename})")
                continue

            print(f"[+] Linking visual in: {file}")
            print(f"    Image: {image_filename}")

            if not dry_run:
                inject_link(filepath, image_filename)
                print("    ✅ Link injected.")
            else:
                print("    [Dry Run] Would inject link.")
            
            linked_count += 1

    print(f"\n[-] Complete. Integrated {linked_count} visuals.")

if __name__ == "__main__":
    dry_run_mode = "--dry-run" in sys.argv
    main(dry_run=dry_run_mode)
