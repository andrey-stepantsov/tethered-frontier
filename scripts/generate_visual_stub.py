import os
import sys
import requests
import base64

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

    print(f"[*] Authenticating with Google AI (REST API)...")

    # 2. Prepare Request
    # Using the REST API directly to avoid SDK version/deprecation issues.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Construct payload for Imagen 3
    payload = {
        "instances": [
            {
                "prompt": STATIC_PROMPT
            }
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "16:9"
        }
    }

    # 3. Generate Content
    print(f"[*] Generating visual with prompt:\n    \"{STATIC_PROMPT}\"")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        # 4. Process Response
        if "predictions" in result and result["predictions"]:
            # The API returns base64 encoded image in 'bytesBase64Encoded'
            prediction = result["predictions"][0]
            b64_image = prediction.get("bytesBase64Encoded")
            
            if b64_image:
                image_data = base64.b64decode(b64_image)
                
                # 5. Save Output
                output_path = os.path.join("content", "assets", OUTPUT_FILENAME)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, "wb") as f:
                    f.write(image_data)
                    
                print(f"[+] Success! Image saved to: {output_path}")
                print(f"[!] Remember to add the prompt to your markdown file as a comment (per CONVENTIONS.md).")
            else:
                print("[-] API returned predictions but no image data found.")
        else:
            print(f"[-] API returned no images. Response: {result}")

    except requests.exceptions.RequestException as e:
        print(f"[-] Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"    Details: {e.response.text}")
    except Exception as e:
        print(f"[-] An error occurred: {e}")

if __name__ == "__main__":
    main()
