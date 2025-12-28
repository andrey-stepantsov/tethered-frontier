import os
import re

# Configuration
CONTENT_DIR = "content"
MARKER = "NEVER display the prompt text to the reader."

def find_missing_visuals():
    # Regex for markdown images: ![alt](url) or ![[wikilink]]
    img_pattern = re.compile(r'!\[.*?\]\(.*?\)|!\[\[.*?\]\]')
    
    # Regex to find HTML comments: <!-- ... -->
    # re.DOTALL allows . to match newlines
    comment_pattern = re.compile(r'<!--(.*?)-->', re.DOTALL)

    if not os.path.exists(CONTENT_DIR):
        print(f"Error: Directory '{CONTENT_DIR}' not found.")
        return

    print(f"Scanning '{CONTENT_DIR}' for missing visual assets...\n")

    found_count = 0

    for root, dirs, files in os.walk(CONTENT_DIR):
        for file in files:
            if not file.endswith(".md"):
                continue
            
            path = os.path.join(root, file)
            
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"Could not read {path}: {e}")
                continue

            # 1. Check if the file contains the Prompt Marker
            if MARKER not in content:
                continue

            # 2. Check if the file already has an image
            if img_pattern.search(content):
                continue

            # 3. Extract the prompt
            comments = comment_pattern.findall(content)
            prompt_text = None

            for c in comments:
                if MARKER in c:
                    # Split lines and remove the marker line to get the raw prompt
                    lines = c.strip().split('\n')
                    cleaned_lines = [line.strip() for line in lines if MARKER not in line]
                    prompt_text = "\n".join(cleaned_lines).strip()
                    break
            
            if prompt_text:
                found_count += 1
                print(f"FILE: {path}")
                print("PROMPT:")
                print(prompt_text)
                print("-" * 40)

    if found_count == 0:
        print("No missing visuals found (or no prompts detected without images).")

if __name__ == "__main__":
    find_missing_visuals()
