import os
import sys
import requests
import base64

# --- CONFIGURATION ---
# Updated to use the available Imagen 4 model found in your list
MODEL_NAME = "imagen-4.0-generate-001"
OUTPUT_FILENAME = "test_surveillance_feed.png"

# Adhering to CONVENTIONS.md: "Surveillance Intercept"
STATIC_PROMPT = (
    "A gritty, low-fidelity surveillance camera feed from inside a rusted industrial spaceship. "
    "Monochromatic green night-vision aesthetic. "
    "Heavy film grain, digital artifacts, and scanlines. "
    "Subject: A worn-out airlock door with scratched warning paint. "
    "HUD overlay text in corner reading 'CAM-04 // O2 LEVEL: CRITICAL'. "
    "Fisheye lens distortion. "
    "Photorealistic but damaged footage quality."
)

def generate_image(prompt, output_path):
    """
    Generates an image using Google Gemini/Imagen REST API and saves it to output_path.
    Returns True if successful, False otherwise.
    """
    # 1. Check Environment
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables.")
        return False

    # 2. Prepare Request
    # Updated URL to use the dynamic MODEL_NAME
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:predict?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Construct payload
    payload = {
        "instances": [
            {
                "prompt": prompt
            }
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "16:9"
        }
    }

    print(f"[*] Sending request to model: {MODEL_NAME}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        # 3. Process Response
        if "predictions" in result and result["predictions"]:
            prediction = result["predictions"][0]
            b64_image = prediction.get("bytesBase64Encoded")
            
            if b64_image:
                image_data = base64.b64decode(b64_image)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, "wb") as f:
                    f.write(image_data)
                    
                print(f"[+] Visual saved to: {output_path}")
                return True
            else:
                print("[-] API returned predictions but no image data found.")
                return False
        else:
            print(f"[-] API returned no images. Response: {result}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"[-] Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"    Details: {e.response.text}")
        return False
    except Exception as e:
        print(f"[-] An error occurred: {e}")
        return False

def main():
    # Wrapper for standalone execution
    output_path = os.path.join("content", "assets", OUTPUT_FILENAME)
    print(f"[*] Generating visual with prompt:\n    \"{STATIC_PROMPT}\"")
    generate_image(STATIC_PROMPT, output_path)

if __name__ == "__main__":
    main()
