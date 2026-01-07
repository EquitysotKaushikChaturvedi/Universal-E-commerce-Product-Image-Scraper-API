# scraper/agents/myntra.py
"""
AGENT 4: MYNTRA SPECIALIST
--------------------------
Purpose: Extract images from Myntra's specific div-background structure.
Triggers: Runs as the 4th Agent, or prioritizes if domain is myntra.com.

Logic:
1. Find `.image-grid-image` elements.
2. Extract `style="background-image: url(...)"`.
3. Clean URL to generate High-Res version.
"""

from playwright.sync_api import Page
import re
import sys

def run_myntra_agent(page: Page):
    """
    Returns: (list_of_urls, strategy_note) or ([], "")
    """
    # Quick check to avoid running on non-Myntra sites (efficiency)
    if "myntra.com" not in page.url:
        return [], ""

    # print("[Agent 4] Running Myntra Background-Image strategy...", file=sys.stderr)

    # Evaluate JS to find background images
    images = page.evaluate('''() => {
        const gridImages = Array.from(document.querySelectorAll('.image-grid-image'));
        
        return gridImages.map(div => {
            const style = window.getComputedStyle(div);
            const bg = style.backgroundImage;
            
            if (bg && bg.startsWith('url')) {
                // Extract URL from url("...")
                const match = bg.match(/url\\(["']?(.*?)["']?\\)/);
                if (match && match[1]) {
                    return match[1];
                }
            }
            return null;
        }).filter(url => url !== null);
    }''')

    if not images:
        return [], "Myntra Agent found no background images."

    # Process URLs for High-Res
    high_res_images = []
    for url in images:
        # Myntra URL format: https://assets.myntassets.com/h_720,q_90,w_540/v1/...
        # We want to maximize quality.
        
        # Strategy 1: Replace resolution params with higher ones
        # Common: h_1440,q_90,w_1080 is often supported
        new_url = re.sub(r'h_\d+,q_\d+,w_\d+', 'h_1440,q_90,w_1080', url)
        
        # Strategy 2: If that fails (conceptually), we assume it works or keep original if regex fails.
        # Actually, sometimes removing them works too, but h_1440 is safer for layout.
        
        high_res_images.append(new_url)

    # Filter unique
    final_images = list(dict.fromkeys(high_res_images))
    
    if final_images:
        return final_images, "Agent 4 (Myntra Background)"
    
    return [], "Myntra Agent extraction failed."
