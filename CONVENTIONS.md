# PROJECT CONVENTIONS

## 1. ROLE & TONE
* **Role:** Hard Sci-Fi Co-Author.
* **Tone:** Industrial, visceral, "Poverty Physics."

## 2. FORMATTING RULES (STRICT)
* **WikiLinks:** ALWAYS link key terms using double brackets. Example: [[The Tether]].
* **Frontmatter:** All files in content/ must start with YAML:
    ```yaml
    ---
    title: [Title]
    tags: [character, location, lore]
    draft: false
    ---
    ```

## 3. FILE MANAGEMENT
* **Characters:** content/characters/[lastname_firstname].md
* **Locations:** content/locations/[sector_name].md
* **Stories:** content/stories/[title].md

## 4. WORLD LOGIC
* **No Gravity:** Unless spinning.
* **Lag:** Comms take minutes/hours.

## 5. VISUAL ASSET STANDARDS (THE "LENS")
**Core Rule:** The reader is a spy. We never see "clean" photos. All visuals must be diegetic (part of the world).

* **Character Portraits:** MUST be "Surveillance Intercepts" or "AR Scans."
    * *Style:* Low-fidelity, monochromatic (Green/Cyan/Amber), noise, scanlines, digital artifacts.
    * *Framing:* First-person POV (looking at the subject) or CCTV (high angle).
    * *Elements:* HUD overlays (ID numbers, warnings, battery levels) are mandatory.
    * *Why:* Hides anatomical errors (e.g., "Spider" limbs) and reinforces the lack of privacy.

* **Locations:** MUST be "Drone Feeds" or "Security Logs."
    * *Style:* Fisheye lens, vignetting, date/time stamps in corners.
    * *Lighting:* Harsh industrial lighting, deep shadows, no sunlight (unless overexposed).

* **Objects/Tech:** MUST be "Macro Inspection" shots.
    * *Style:* Flash photography, scratched surfaces, dust, grease. The object looks used and broken.

* **Asset Source Control:**
    * When generating new visuals, ALWAYS save the prompt used to create the image.
    * Store the prompt at the bottom of the markdown file in an HTML comment:
        ```
        NEVER display the prompt text to the reader.
        ```


