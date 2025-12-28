import os
import requests
import json

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables.")
        return

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    print(f"[*] Querying available models from: {url.split('?')[0]}...")

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        models = data.get("models", [])
        print(f"[*] Found {len(models)} models:\n")
        
        for m in models:
            name = m.get("name")
            version = m.get("version")
            display_name = m.get("displayName")
            methods = m.get("supportedGenerationMethods", [])
            
            print(f"Name: {name}")
            print(f"Display Name: {display_name}")
            print(f"Version: {version}")
            print(f"Supported Methods: {methods}")
            print("-" * 40)

    except requests.exceptions.RequestException as e:
        print(f"[-] Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"    Details: {e.response.text}")
    except Exception as e:
        print(f"[-] An error occurred: {e}")

if __name__ == "__main__":
    main()
