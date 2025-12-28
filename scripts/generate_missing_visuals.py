import os
import re
import sys
import generate_visual_stub

# CONFIGURATION
CONTENT_DIR = "content"
ASSETS_DIR = os.path.join(CONTENT_DIR, "assets", "images")
MARKER = "NEVER display the prompt text to the reader."
# STRICT PNG ENFORCEMENT
SUPPORTED_EXTENSIONS = [".png"]

def clean_prompt_text(raw_text):
    """
    Cleans up the prompt text extracted from the markdown.
    Removes markdown block quotes (>), newlines, and extra spaces.
    """
    text = raw_text.replace("\n", " ")
    text = text.replace(">", "")
    text = re.sub(r'\s+', ' ', text) # Collapse multiple spaces
    return text.strip()

def image_exists(filename):
    """
    Checks if the image exists in the assets directory.
    """
    return os.path.exists(os.path.join(ASSETS_DIR, filename))

def find_and_generate(full_auto=False, dry_run=False):
    print(f"[-] Scanning '{CONTENT_DIR}' for missing visuals...")
    
    if dry_run:
        print("[-] Mode: DRY RUN (No images will be generated)")
    elif full_auto:
        print("[-] Mode: FULL AUTO (No confirmation required)")
    else:
        print("[-] Mode: INTERACTIVE (Use --auto to skip confirmations)")
    
    if not os.path.exists(ASSETS_DIR):
        if dry_run:
            print(f"    [Dry Run] Would create directory: {ASSETS_DIR}")
        else:
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
            
            # Regex to find blocks. 
            # We look for TARGET: ... PROMPT: ... 
            # If no TARGET found, we look for just PROMPT: ... and use filename.
            # This regex iterates through ALL prompt blocks in the file.
            block_pattern = re.compile(r"(?:TARGET:\s*(?P<target>[\w\-\.]+).*?)?PROMPT:\s*(?P<prompt>.*?)(?:-->|NEVER)", re.DOTALL | re.IGNORECASE)
            
            matches = list(block_pattern.finditer(content))
            
            if not matches:
                continue

            for match in matches:
                raw_target = match.group("target")
                raw_prompt = match.group("prompt")
                
                clean_prompt = clean_prompt_text(raw_prompt)
                
                if not clean_prompt:
                    continue

                # Determine Target Filename
                if raw_target:
                    base_name = raw_target.strip()
                else:
                    # Fallback to filename if no explicit target
                    base_name = os.path.splitext(file)[0]
                
                target_filename = f"{base_name}.png"
                image_path = os.path.join(ASSETS_DIR, target_filename)
                
                # Check if Asset Exists
                if image_exists(target_filename):
                    continue
                
                # Generate
                print(f"\n[+] Missing visual detected for: {file}")
                print(f"    Target: {target_filename}")
                print(f"    Prompt: {clean_prompt[:60]}...")
                
                if dry_run:
                    print("    [Dry Run] Would generate image now.")
                    generated_count += 1
                    continue

                if not full_auto:
                    confirm = input("    Generate this image? [y/N] ").strip().lower()
                    if confirm != 'y':
                        print("    [Skipped]")
                        continue

                # Call the generation stub
                success = generate_visual_stub.generate_image(clean_prompt, image_path)
                
                if success:
                    print(f"    ✅ Generated and saved.")
                    generated_count += 1
                else:
                    print(f"    ❌ Generation failed.")

    if dry_run:
        print(f"\n[-] Dry run complete. Would have generated {generated_count} new images.")
    else:
        print(f"\n[-] Scan complete. Generated {generated_count} new images.")

if __name__ == "__main__":
    full_auto_mode = False
    dry_run_mode = False
    
    if "--auto" in sys.argv:
        full_auto_mode = True
    if "--dry-run" in sys.argv:
        dry_run_mode = True
    
    find_and_generate(full_auto=full_auto_mode, dry_run=dry_run_mode)
