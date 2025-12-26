import os
import re
import sys

CONTENT_DIR = 'content'

def build_index(root_dir):
    """
    Scans the root_dir recursively.
    Returns a set of valid link targets (lowercase).
    Includes:
    - filename (e.g., 'image.png', 'note.md')
    - filename without extension (e.g., 'note')
    - relative path (e.g., 'folder/note.md')
    - relative path without extension (e.g., 'folder/note')
    """
    valid_targets = set()
    
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            # Full path relative to content root
            full_path = os.path.join(dirpath, f)
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
            
    return valid_targets

def check_content(root_dir, valid_targets):
    """
    Scans .md files in root_dir for [[WikiLinks]].
    Checks if the target exists in valid_targets.
    Returns a list of (file_path, missing_target) tuples.
    """
    broken_links = []
    # Regex to capture [[Target]] or [[Target|Alias]]
    # Non-greedy match for content inside brackets
    link_pattern = re.compile(r'\[\[(.*?)\]\]')
    
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if not f.endswith('.md'):
                continue
            
            file_path = os.path.join(dirpath, f)
            
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
                
                # 3. Clean whitespace
                target = target.strip()
                
                # Skip empty targets (e.g. [[#anchor]] links to self, or empty [[]])
                if not target:
                    continue
                
                # 4. Check validity
                if target.lower() not in valid_targets:
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
            print(f"File:   {file_path}")
            print(f"Target: [[{target}]]")
            print("-" * 40)
        sys.exit(1)
    else:
        print("\n✅ No broken links found")
        sys.exit(0)

if __name__ == "__main__":
    main()
