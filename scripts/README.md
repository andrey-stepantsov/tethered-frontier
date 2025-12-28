# Automation Scripts

This directory contains Python scripts used to automate content creation, asset generation, and maintenance for the **Tethered Frontier** World Bible.

## Prerequisites

1. **Python 3.x**
2. **Dependencies:**
   ```bash
   pip install requests
   ```
3. **Environment Variables:**
   * `GEMINI_API_KEY`: Required for image generation. Get one from Google AI Studio.

---

## Core Workflow

### 1. Create New Page (`new_page.py`)
**The primary tool for authors.** Creates a new markdown file with correct frontmatter and optionally generates a visual asset.

* **Usage:**
  ```bash
  python3 scripts/new_page.py <category> <title>
  ```
* **Example:**
  ```bash
  python3 scripts/new_page.py characters "Jaxon The Welder"
  ```
* **Features:**
  * Enforces **kebab-case** filenames (e.g., `jaxon-the-welder.md`).
  * Prevents overwriting existing files.
  * Prompts to generate a "Surveillance Feed" style image using Google Imagen.
  * Saves images to `content/assets/images/`.
  * Adds the generation prompt as a hidden HTML comment in the markdown.

### 2. Generate Visual Stub (`generate_visual_stub.py`)
Handles the connection to the Google Imagen API to generate diegetic "surveillance" visuals.

* **Usage:**
  * **Imported:** Used by `new_page.py` to generate specific character/location images.
  * **Standalone:** Runs a test generation using a static prompt to verify API connectivity.
    ```bash
    python3 scripts/generate_visual_stub.py
    ```
* **Configuration:**
  * Model: `imagen-4.0-generate-001`
  * Output: `content/assets/images/`

### 3. Generate Missing Visuals (`generate_missing_visuals.py`)
Batch processor that scans existing content for defined prompts that lack corresponding image files.

* **Usage:**
  ```bash
  python3 scripts/generate_missing_visuals.py
  ```
* **Logic:**
  * Scans for the `NEVER display the prompt` marker.
  * Extracts the prompt text from the HTML comment.
  * Identifies the target filename (checking `TARGET:` tags, then Wikilinks, then filename).
  * Generates the image if it does not exist in `content/assets/images/`.

---

## Maintenance & Auditing

### 4. Check Links (`check_links.py`)
Scans all Markdown files in `content/` to ensure every Wikilink `[[Link]]` points to a valid file or anchor.

* **Usage:**
  ```bash
  python3 scripts/check_links.py
  ```
* **Logic:**
  * Builds an index of all valid slugs and filenames.
  * Ignores files marked `draft: true`.
  * Reports broken links with file paths.

### 5. Audit Visual Assets (`audit_visuals.py`)
A comprehensive check of the relationship between Markdown files and Image assets.

* **Usage:**
  ```bash
  python3 scripts/audit_visuals.py
  ```
* **Logic:**
  * Scans for the `TARGET: filename` marker inside HTML comments.
  * Verifies if the target image exists in `content/assets/`.
  * Reports:
    * **Pending Generation:** Prompt exists, but image is missing.
    * **Missing Target:** Prompt block exists, but no `TARGET:` defined.
    * **Duplicate Targets:** Multiple files claiming the same image.

### 6. Find Missing Visuals (`find_missing_visuals.py`)
A lighter scanner that specifically looks for files containing the "Prompt Marker" but lacking an actual image link.

* **Usage:**
  ```bash
  python3 scripts/find_missing_visuals.py
  ```
* **Logic:**
  * Looks for the string: `NEVER display the prompt text to the reader.`
  * Checks if the file contains an image link `![...]`.
  * If the marker exists but the image link does not, it prints the hidden prompt.

---

## Utilities

### 7. List Models (`list_models.py`)
Queries the Google Gemini API to list available models. Useful for debugging API access or checking for new model versions.

* **Usage:**
  ```bash
  python3 scripts/list_models.py
  ```
