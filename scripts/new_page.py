import os
import sys
import re
import generate_visual_stub  # Import the image generator

# CONFIGURATION
CONTENT_DIR = "content"
# Updated to save images in content/assets/images/
ASSETS_DIR = os.path.join(CONTENT_DIR, "assets", "images")
# Removed 'assets' from categories as it's not for markdown pages
CATEGORIES = ["characters", "lore", "locations", "stories"]

def slugify(text):
    """
    Converts a title into a filename-safe slug.
    Example: "The Rusty Anchor" -> "the-rusty-anchor"
    """
    text = text.lower()
    # Remove characters that aren't alphanumerics, spaces, or hyphens
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    # Replace whitespace or existing hyphens with a single hyphen
    text = re.sub(r'[\s-]+', '-', text)
    # Strip leading/trailing hyphens
    return text.strip('-')

def construct_prompt(category, title):
    """
    Constructs a prompt based on CONVENTIONS.md rules.
    """
    base_style = (
        "A gritty, low-fidelity surveillance camera feed from inside a rusted industrial spaceship. "
        "Monochromatic green night-vision aesthetic. "
        "Heavy film grain, digital artifacts, and scanlines. "
        "Fisheye lens distortion. "
        "Photorealistic but damaged footage quality. "
    )
    
    if category == "characters":
        subject = f"Subject: A sci-fi character named '{title}', wearing worn industrial space gear. "
        details = "Face partially obscured by shadows or gear. HUD overlay with ID numbers."
    elif category == "locations":
        subject = f"Subject: A wide shot of a sci-fi location named '{title}'. Industrial, cramped, dirty. "
        details = "HUD overlay with sector coordinates and environmental warnings."
    else:
        # Covers lore, stories, etc.
        subject = f"Subject: An object or scene representing '{title}'. "
        details = "Macro inspection style, flash photography look."

    return base_style + subject + details

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
    if os.path.exists(filepath):
        print(f"❌ ABORT: File already exists at '{filepath}'")
        print("   To edit this file, open it manually.")
        sys.exit(1)

    # 2. PREPARE FRONTMATTER
    tag = category[:-1] if category.endswith('s') else category
    
    # 3. IMAGE GENERATION LOGIC
    image_markdown = ""
    prompt_comment = ""
    
    # Added 'lore' to the list of categories that prompt for visuals
    if category in ["characters", "locations", "lore"]:
        print(f"\n[?] Generate a 'Surveillance Feed' visual for this {tag}? (y/N)")
        choice = input("> ").strip().lower()
        
        if choice == 'y':
            image_filename = f"{slugify(title)}.png"
            image_path = os.path.join(ASSETS_DIR, image_filename)
            prompt = construct_prompt(category, title)
            
            print(f"[*] Attempting to generate visual...")
            # Ensure assets directory exists
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            
            success = generate_visual_stub.generate_image(prompt, image_path)
            
            if success:
                # Quartz prefers just the filename for Wikilinks
                image_markdown = f"![[{image_filename}]]\n\n"
                prompt_comment = f"\n<!--\nNEVER display the prompt text to the reader.\nPROMPT: {prompt}\n-->"
            else:
                print("[!] Skipping image inclusion due to generation failure.")

    content = f"""---
title: {title}
tags:
  - {tag}
aliases: ["{title}"]
draft: false
---

# {title}

{image_markdown}
{prompt_comment}
"""

    # 4. CREATE FILE
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
    
    cat_arg = sys.argv[1]
    
    # Handle title if passed as multiple arguments without quotes
    if len(sys.argv) > 3:
        title_arg = " ".join(sys.argv[2:])
    else:
        title_arg = sys.argv[2]
    
    create_page(cat_arg, title_arg)
