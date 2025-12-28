import os
import sys
import google.generativeai as genai
from PIL import Image

# --- CONFIGURATION ---
# In the real script, these would be dynamic based on the file tags.
OUTPUT_FILENAME = "test_surveillance_feed.png"

# Adhering to CONVENTIONS.md: "Surveillance Intercept"
# Style: Low-fidelity, monochromatic, noise, scanlines.
STATIC_PROMPT = (
    "A gritty, low-fidelity surveillance camera feed from inside a rusted industrial spaceship. "
    "Monochromatic green night-vision aesthetic. "
    "Heavy film grain, digital artifacts, and scanlines. "
    "Subject: A worn-out airlock door with scratched warning paint. "
    "HUD overlay text in corner reading 'CAM-04 // O2 LEVEL: CRITICAL'. "
    "Fisheye lens distortion. "
    "Photorealistic but damaged footage quality."
)

def main():
    # 1. Check Environment
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables.")
        sys.exit(1)

    print(f"[*] Authenticating with Google AI...")
    genai.configure(api_key=api_key)

    # 2. Initialize Model (Using Imagen 3)
    # Note: Model names may vary by region/access. Common: 'imagen-3.0-generate-001'
    try:
        model = genai.ImageGenerationModel("imagen-3.0-generate-001")
    except AttributeError:
        # Fallback or specific error if the SDK version is older
        print("Error: Could not initialize ImageGenerationModel. Ensure google-generativeai is up to date.")
        sys.exit(1)

    # 3. Generate Content
    print(f"[*] Generating visual with prompt:\n    \"{STATIC_PROMPT}\"")
    
    try:
        response = model.generate_images(
            prompt=STATIC_PROMPT,
            number_of_images=1,
            aspect_ratio="16:9", 
            safety_filter_level="block_only_high",
            person_generation="allow_adult", 
        )
        
        if response.images:
            image = response.images[0]
            
            # 4. Save Output
            output_path = os.path.join("content", "assets", OUTPUT_FILENAME)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            image.save(output_path)
            print(f"[+] Success! Image saved to: {output_path}")
            print(f"[!] Remember to add the prompt to your markdown file as a comment (per CONVENTIONS.md).")
        else:
            print("[-] API returned no images.")

    except Exception as e:
        print(f"[-] Generation failed: {e}")

if __name__ == "__main__":
    main()
