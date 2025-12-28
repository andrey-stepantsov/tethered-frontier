import os
import re
import sys

# CONFIGURATION
CONTENT_DIR = "content"
ASSETS_DIR = os.path.join(CONTENT_DIR, "assets", "images")
MARKER = "NEVER display the prompt text to the reader."
# Only support PNG now
SUPPORTED_EXTENSIONS = [".png"]

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

def get_existing_link(content):
    """
    Returns the filename inside the first image wikilink found, or None.
    """
    match = re.search(r"!\[\[(.*?)(?:\|.*?)?\]\]", content)
    if match:
        return match.group(1)
    return None

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

def update_link(filepath, content, old_link_name, new_link_name):
    """
    Replaces the old link filename with the new one, preserving alt text if present.
    """
    # Regex for the full tag: ![[old_link_name(|alt)]]
    tag_pattern = re.compile(r"!\[\[" + re.escape(old_link_name) + r"(?:\|.*?)?\]\]")
    
    def replacer(match):
        full_match = match.group(0)
        if "|" in full_match:
            # extract alt text. full_match ends with ]]
            # split gives ['![[filename', 'alt]]']
            alt = full_match.split("|", 1)[1][:-2]
            return f"![[{new_link_name}|{alt}]]"
        else:
            return f"![[{new_link_name}]]"

    new_content = tag_pattern.sub(replacer, content, count=1)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

def main(dry_run=False):
    print(f"[-] Scanning '{CONTENT_DIR}' for visual integration...")
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

            basename = get_target_basename(content, file)
            
            # We only care about PNGs now
            png_filename = basename + ".png"
            png_exists = os.path.exists(os.path.join(ASSETS_DIR, png_filename))

            existing_link_name = get_existing_link(content)

            if existing_link_name:
                # Link exists. Check if it needs updating.
                _, ext = os.path.splitext(existing_link_name)
                if ext.lower() != ".png":
                    if png_exists:
                        print(f"[~] Updating extension in: {file}")
                        print(f"    {existing_link_name} -> {png_filename}")
                        if not dry_run:
                            update_link(filepath, content, existing_link_name, png_filename)
                            print("    ✅ Updated.")
                        else:
                            print("    [Dry Run] Would update.")
                        linked_count += 1
                    else:
                        print(f"[!] Found non-PNG link '{existing_link_name}' in {file}, but '{png_filename}' does not exist.")
                else:
                    # It is already PNG.
                    pass
            else:
                # No link exists. Inject if PNG exists.
                if png_exists:
                    print(f"[+] Linking visual in: {file}")
                    print(f"    Image: {png_filename}")
                    if not dry_run:
                        inject_link(filepath, png_filename)
                        print("    ✅ Link injected.")
                    else:
                        print("    [Dry Run] Would inject link.")
                    linked_count += 1
                else:
                    print(f"[!] Image missing for: {file} (Expected: {png_filename})")

    print(f"\n[-] Complete. Processed {linked_count} updates/injections.")

if __name__ == "__main__":
    dry_run_mode = "--dry-run" in sys.argv
    main(dry_run=dry_run_mode)
