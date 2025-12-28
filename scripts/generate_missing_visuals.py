import os
import re
import generate_visual_stub

# CONFIGURATION
CONTENT_DIR = "content"
ASSETS_DIR = os.path.join(CONTENT_DIR, "assets", "images")
MARKER = "NEVER display the prompt text to the reader."

def clean_prompt_text(raw_text):
    """
    Cleans up the prompt text extracted from the markdown.
    Removes markdown block quotes (>), newlines, and extra spaces.
    """
    text = raw_text.replace("\n", " ")
    text = text.replace(">", "")
    text = re.sub(r'\s+', ' ', text) # Collapse multiple spaces
    return text.strip()

def get_target_filename(content, filename):
    """
    Determines the target image filename.
    Priority 1: 'TARGET: filename' inside comments.
    Priority 2: First Wikilink '![[filename]]'.
    Priority 3: Derive from markdown filename (e.g. page.md -> page.png).
    """
    # 1. Check for explicit TARGET:
    target_match = re.search(r"TARGET:\s*([\w\-\.]+)", content, re.IGNORECASE)
    if target_match:
        name = target_match.group(1).strip()
        # Append extension if missing (default to png for generation)
        if not os.path.splitext(name)[1]:
            name += ".png"
        return name

    # 2. Check for existing Wikilink
    link_match = re.search(r"!\[\[(.*?)\]\]", content)
    if link_match:
        return link_match.group(1).strip()

    # 3. Fallback
    return filename.replace(".md", ".png")

def find_and_generate():
    print(f"[-] Scanning '{CONTENT_DIR}' for missing visuals...")
    
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)

    generated_count = 0
    
    for root, _, files in os.walk(CONTENT_DIR):
        for file in files:
            if not file.endswith(".md"):
                continue
                
            filepath = os.path.join(root, file)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Skip files without the prompt marker
            if MARKER not in content:
                continue
            
            # 1. Extract the Prompt
            # Looks for "PROMPT:" followed by text until the closing comment or marker
            # We use a non-greedy match for the content
            prompt_match = re.search(r"PROMPT:(.*?)(?:-->|NEVER)", content, re.DOTALL)
            
            if not prompt_match:
                print(f"[!] Marker found but no PROMPT section in: {file}")
                continue
            
            raw_prompt = prompt_match.group(1)
            clean_prompt = clean_prompt_text(raw_prompt)
            
            if not clean_prompt:
                print(f"[!] Empty prompt found in: {file}")
                continue

            # 2. Determine Target Filename
            target_filename = get_target_filename(content, file)
            image_path = os.path.join(ASSETS_DIR, target_filename)
            
            # 3. Check if Asset Exists
            if os.path.exists(image_path):
                continue
            
            # 4. Generate
            print(f"\n[+] Missing visual detected for: {file}")
            print(f"    Target: {target_filename}")
            print(f"    Prompt: {clean_prompt[:60]}...")
            
            success = generate_visual_stub.generate_image(clean_prompt, image_path)
            
            if success:
                print(f"    ✅ Generated and saved.")
                generated_count += 1
            else:
                print(f"    ❌ Generation failed.")

    print(f"\n[-] Scan complete. Generated {generated_count} new images.")

if __name__ == "__main__":
    find_and_generate()
