import os
import re
import sys

# CONFIGURATION
CONTENT_DIR = "content"
ASSETS_DIR = os.path.join(CONTENT_DIR, "assets", "images")
MARKER = "NEVER display the prompt text to the reader."
# Only support PNG now
SUPPORTED_EXTENSIONS = [".png"]

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
    link_line = f"\n![[{image_filename}]]\n"
    
    lines.insert(insert_index, link_line)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)

def update_link_in_content(content, old_tag, new_filename):
    """
    Replaces the old tag with a new tag pointing to new_filename, preserving alt text.
    Returns the updated content string.
    """
    if "|" in old_tag:
        # extract alt text. old_tag ends with ]]
        # split gives ['![[filename', 'alt]]']
        alt = old_tag.split("|", 1)[1][:-2]
        new_tag = f"![[{new_filename}|{alt}]]"
    else:
        new_tag = f"![[{new_filename}]]"
    
    return content.replace(old_tag, new_tag)

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

            # 1. Find all targets defined in the file
            # Matches "TARGET: some-name"
            targets = re.findall(r"TARGET:\s*([\w\-\.]+)", content, re.IGNORECASE)
            
            # If no explicit targets, assume the file itself is the target (if it has a prompt marker)
            if not targets:
                targets = [os.path.splitext(file)[0]]
            
            file_modified = False
            
            for target_base in targets:
                png_filename = f"{target_base}.png"
                png_path = os.path.join(ASSETS_DIR, png_filename)
                
                if not os.path.exists(png_path):
                    # If the PNG doesn't exist, we can't link it yet.
                    # (The audit script handles reporting missing assets)
                    continue
                    
                # Check for existing link to this target (any extension)
                # We want to match ![[target_base]] or ![[target_base.jpg]] or ![[target_base.png]]
                # But NOT ![[target_base_other]]
                
                # Regex explanation:
                # !\[\[              Match opening brackets
                # target_base        Match the specific target name
                # (?:\.[a-zA-Z0-9]+)? Match optional extension (.jpg, .png, etc)
                # (?:\|.*?)?         Match optional alt text (| description)
                # \]\]               Match closing brackets
                
                link_pattern = re.compile(r"!\[\[" + re.escape(target_base) + r"(?:\.[a-zA-Z0-9]+)?(?:\|.*?)?\]\]")
                
                match = link_pattern.search(content)
                
                if match:
                    existing_tag = match.group(0)
                    
                    # Check if it's already the correct PNG
                    # We check if the existing tag contains the exact png filename
                    if f"![[{png_filename}]]" in existing_tag or f"![[{png_filename}|" in existing_tag:
                        continue
                    
                    # It's a link to the target, but wrong extension (e.g. .jpeg) or missing extension
                    print(f"[~] Updating link in {file}: {existing_tag} -> {png_filename}")
                    
                    if not dry_run:
                        content = update_link_in_content(content, existing_tag, png_filename)
                        file_modified = True
                    else:
                        print("    [Dry Run] Would update.")
                    
                    linked_count += 1
                else:
                    # Link doesn't exist, inject it
                    print(f"[+] Injecting link for {png_filename} in {file}")
                    if not dry_run:
                        # For injection, we need to write to file immediately or handle complex insertion logic.
                        # Since we are iterating targets, let's use the helper but we need to be careful 
                        # about 'content' variable drift if we inject multiple times.
                        # Simplest approach: Write content so far, then call inject_link which re-reads.
                        # BUT inject_link inserts at top.
                        
                        # If we have modified content (updates), save it first.
                        if file_modified:
                            with open(filepath, "w", encoding="utf-8") as f:
                                f.write(content)
                            file_modified = False # Reset flag
                        
                        inject_link(filepath, png_filename)
                        
                        # Re-read content for next iteration in this file
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = f.read()
                    else:
                        print("    [Dry Run] Would inject link.")
                    linked_count += 1

            # Final save if modifications were made (updates only, no injections)
            if file_modified and not dry_run:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)

    print(f"\n[-] Complete. Processed {linked_count} updates/injections.")

if __name__ == "__main__":
    dry_run_mode = "--dry-run" in sys.argv
    main(dry_run=dry_run_mode)
