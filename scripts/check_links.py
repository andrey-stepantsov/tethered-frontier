import os
import re
import sys

# Determine the absolute path to the 'content' directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CONTENT_DIR = os.path.join(PROJECT_ROOT, 'content')

def quartz_slugify(text):
    """
    Mimics Quartz slugification logic to match [[Wiki Links]] to kebab-case filenames.
    """
    # Remove invalid chars
    text = text.replace('?', '').replace('#', '').replace('%', '')
    # Replace spaces with hyphens
    text = text.replace(' ', '-')
    # Lowercase
    return text.lower()

def is_draft(file_path):
    """
    Checks if a markdown file has 'draft: true' in its frontmatter.
    Handles:
      draft: true
      draft: "true"
      draft: 'true'
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                # Regex explanation:
                # ^draft:       Start of line, key 'draft:'
                # \s*           Optional whitespace
                # ["']?         Optional quote
                # true          Literal 'true' (case insensitive via flag)
                # ["']?         Optional quote
                if re.search(r'^draft:\s*["\']?true["\']?', frontmatter, re.MULTILINE | re.IGNORECASE):
                    return True
    except Exception:
        pass
    return False

def build_index(root_dir):
    """
    Scans the root_dir recursively.
    Returns a set of valid link targets (lowercase).
    """
    valid_targets = set()
    
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            full_path = os.path.join(dirpath, f)
            
            # Skip drafts for .md files
            if f.endswith('.md') and is_draft(full_path):
                continue

            # Full path relative to content root
            rel_path = os.path.relpath(full_path, root_dir)
            
            # Normalize inputs
            rel_path_lower = rel_path.lower()
            filename_lower = f.lower()
            
            # 1. Exact filename (e.g. "image.png")
            valid_targets.add(filename_lower)
            
            # 2. Filename without extension (e.g. "image")
            name_no_ext = os.path.splitext(filename_lower)[0]
            valid_targets.add(name_no_ext)
            
            # 3. Relative path (e.g. "assets/image.png")
            valid_targets.add(rel_path_lower)
            
            # 4. Relative path without extension (e.g. "assets/image")
            rel_path_no_ext = os.path.splitext(rel_path_lower)[0]
            valid_targets.add(rel_path_no_ext)

            # 5. Folder support (index.md)
            # If this file is 'index.md', then the parent folder is a valid target
            if filename_lower == 'index.md':
                # parent folder name relative to content root
                parent_folder = os.path.dirname(rel_path_lower)
                if parent_folder and parent_folder != '.':
                    valid_targets.add(parent_folder)
                    # Also add the folder name itself (not full path) if unique?
                    # Quartz usually resolves [[Folder]] to .../Folder/index.md
                    valid_targets.add(os.path.basename(parent_folder))
            
    return valid_targets

def check_content(root_dir, valid_targets):
    """
    Scans .md files in root_dir for [[WikiLinks]].
    Checks if the target exists in valid_targets.
    Returns a list of (file_path, missing_target) tuples.
    """
    broken_links = []
    # Regex to capture [[Target]] or [[Target|Alias]]
    link_pattern = re.compile(r'\[\[(.*?)\]\]', re.DOTALL)
    
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if not f.endswith('.md'):
                continue
            
            file_path = os.path.join(dirpath, f)
            
            # Optional: Skip checking links INSIDE draft files
            if is_draft(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")
                continue
            
            matches = link_pattern.findall(content)
            for match in matches:
                # 1. Handle Alias: [[Target|Alias]] -> Target
                target = match.split('|')[0]
                
                # 2. Handle Anchor: [[Target#Section]] -> Target
                target = target.split('#')[0]
                
                # 3. Clean whitespace and newlines
                target = target.strip()
                
                # Skip empty targets
                if not target:
                    continue
                
                # 4. Check validity
                # Check exact match (lowercase) OR slugified match
                if (target.lower() not in valid_targets) and (quartz_slugify(target) not in valid_targets):
                    broken_links.append((file_path, target))
                    
    return broken_links

def main():
    if not os.path.exists(CONTENT_DIR):
        print(f"Error: Directory '{CONTENT_DIR}' does not exist.")
        sys.exit(1)

    print(f"Building index from '{CONTENT_DIR}'...")
    index = build_index(CONTENT_DIR)
    
    print(f"Scanning .md files in '{CONTENT_DIR}' for broken links...")
    broken_links = check_content(CONTENT_DIR, index)
    
    if broken_links:
        print(f"\nFound {len(broken_links)} broken links:")
        print("-" * 40)
        for file_path, target in broken_links:
            # Make file path relative for cleaner output
            rel_file = os.path.relpath(file_path, PROJECT_ROOT)
            print(f"File:   {rel_file}")
            print(f"Target: [[{target}]]")
            print("-" * 40)
        sys.exit(1)
    else:
        print("\n✅ No broken links found")
        sys.exit(0)

if __name__ == "__main__":
    main()
