# scraper/agents/context.py
"""
AGENT 2: CONTEXT (PRODUCT-DRIVEN)
---------------------------------
Purpose: Handle modern/dispersed layouts where gallery is implicit.
Strategy:
1. Locate Product Title (H1/H2).
2. Scan visually compatible images near the Title.
3. Heavily filter "Related", "Upsell", "Recommendations".
4. Score images based on DOM proximity to Title.
"""

from playwright.sync_api import Page
import re
import sys

def run_context_agent(page: Page):
    """
    Returns: (list_of_urls, note) or (None, reason)
    """
    print("[Agent 2] Context Analysis started...", file=sys.stderr)
    
    # 1. Identify Product Title
    # Try H1 first, then H2 with class "product" or "title"
    title_text = page.evaluate('''() => {
        let h1 = document.querySelector('h1');
        if (h1 && h1.innerText.length > 5) return h1.innerText.trim();
        
        let h2s = Array.from(document.querySelectorAll('h2, .product-title, .pdp-title'));
        if (h2s.length > 0) return h2s[0].innerText.trim();
        return "";
    }''')
    
    if not title_text:
        return [], "Context: No Product Title found to anchor search."

    print(f"[Agent 2] Anchoring on title: '{title_text}'", file=sys.stderr)

    # 2. Extract & Score
    # We execute complex logic in browser to traverse DOM
    candidates = page.evaluate(f'''() => {{
        const titleText = "{title_text.replace('"', '')}";
        const h1 = document.querySelector('h1') || document.querySelector('h2');
        if (!h1) return [];

        const allImgs = Array.from(document.querySelectorAll('img'));
        const candidates = [];

        // Helper: Check if element is inside a "bad" container
        function isClean(el) {{
            const badKeywords = ['related', 'recommend', 'suggest', 'like', 'similar', 'footer', 'nav', 'header', 'promo'];
            let curr = el;
            while (curr && curr !== document.body) {{
                if (curr.id && badKeywords.some(k => curr.id.toLowerCase().includes(k))) return false;
                if (curr.className && typeof curr.className === 'string' && badKeywords.some(k => curr.className.toLowerCase().includes(k))) return false;
                
                // Specific Check for "You May Also Like" headers
                curr = curr.parentElement;
            }}
            return true;
        }}

        allImgs.forEach(img => {{
            if (!img.src || img.src.includes('svg') || img.src.includes('base64')) return;
            if (img.naturalWidth < 400 || img.naturalHeight < 400) return; // Min size 400x400 for Context
            
            // Filter out strict noise
            if (!isClean(img)) return;

            // Score by vertical distance from H1
            // We want images that start roughly at same Y as H1, or slightly below.
            const h1Rect = h1.getBoundingClientRect();
            const imgRect = img.getBoundingClientRect();

            // Distance metric: simple dy
            const dy = Math.abs(imgRect.top - h1Rect.top);
            
            // If image is WAY below H1 (e.g. 2000px), it's potentially related/reviews
            if (imgRect.top > h1Rect.top + 2000) return; 

            // Priority: Images visible in initial viewport or just below
            candidates.push({{
                src: img.currentSrc || img.src,
                score: dy, // Lower is better (closer to title)
                width: img.naturalWidth
            }});
        }});

        // Sort by proximity (score asc) and size (width desc)
        candidates.sort((a, b) => a.score - b.score);

        // Dedupe
        const unique = new Set();
        return candidates.map(c => c.src).filter(url => {{
            if (unique.has(url)) return false;
            unique.add(url);
            return true;
        }});
    }}''')

    if candidates:
        # Limit to top 8 images to avoid clutter
        final_list = candidates[:8]
        return final_list, f"Context: Found {len(final_list)} images near title '{title_text[:20]}...'"
    
    return [], "Context: No clean images found near title."
