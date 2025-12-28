import os
import sys
import re

# CONFIGURATION
CONTENT_DIR = "content"
# Allowed categories based on folder structure
CATEGORIES = ["characters", "lore", "locations", "stories", "assets"]

def slugify(text):
    """
    Converts a title into a filename-safe slug.
    Example: "The Rusty Anchor" -> "the-rusty-anchor"
    """
    text = text.lower()
    # Remove characters that aren't alphanumerics, spaces, or hyphens
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    # Replace whitespace with a single hyphen
    text = re.sub(r'[\s]+', '-', text)
    # Strip leading/trailing hyphens
    return text.strip('-')

def create_page(category, title):
    # Basic validation
    if category not in CATEGORIES:
        print(f"Error: Category '{category}' is not recognized.")
        print(f"Valid categories: {', '.join(CATEGORIES)}")
        return

    # Generate filename and path
    filename = f"{slugify(title)}.md"
    filepath = os.path.join(CONTENT_DIR, category, filename)

    # 1. THE SAFETY CHECK
    # This prevents accidental overwrites of existing work.
    if os.path.exists(filepath):
        print(f"❌ ABORT: File already exists at '{filepath}'")
        print("   To edit this file, open it manually.")
        sys.exit(1)

    # 2. PREPARE FRONTMATTER
    # Heuristic: singularize tag (characters -> character)
    tag = category[:-1] if category.endswith('s') else category
    
    content = f"""---
title: {title}
tags:
  - {tag}
aliases: ["{title}"]
draft: true
---

# {title}

"""

    # 3. CREATE FILE
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ SUCCESS: Created new page at '{filepath}'")
        print(f"   Title: {title}")
        print(f"   Alias: {title}")
        print(f"   Tag:   {tag}")

    except Exception as e:
        print(f"Error creating file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/new_page.py <category> <title>")
        print("Example: python3 scripts/new_page.py characters \"Captain Vance\"")
        print(f"Valid Categories: {', '.join(CATEGORIES)}")
        sys.exit(1)
    
    # argv[1] is category, argv[2] is title
    cat_arg = sys.argv[1]
    
    # Handle title if passed as multiple arguments without quotes
    if len(sys.argv) > 3:
        title_arg = " ".join(sys.argv[2:])
    else:
        title_arg = sys.argv[2]
    
    create_page(cat_arg, title_arg)
