# scraper/agents/visual.py
"""
AGENT 3: HIGH-CONFIDENCE VISUAL (LAST RESORT)
---------------------------------------------
Purpose: Recover images when DOM is non-semantic but visuals are clear.
Strategy:
1. Scan ONLY the FIRST product viewport (top 1500px).
2. Rank images by: Size, Center Alignment.
3. CRITERIA:
   - Must be large (>450px).
   - Must NOT be in "related" containers.
   - If multiple images found, they usually share dimensions or path patterns.
"""

from playwright.sync_api import Page
import sys

def run_visual_agent(page: Page):
    """
    Returns: (list_of_urls, note) or ([], "")
    """
    print("[Agent 3] Visual Analysis started...", file=sys.stderr)
    
    candidates = page.evaluate('''() => {
        const candidates = [];
        const imgs = Array.from(document.querySelectorAll('img'));
        const viewportHeight = window.innerHeight;
        const viewportWidth = window.innerWidth;
        
        // Helper: Is clean?
        function isClean(el) {
            const badKeywords = ['related', 'recommend', 'suggest', 'footer', 'nav', 'header', 'instagram', 'social'];
            let curr = el;
            while (curr && curr !== document.body) {
                if (curr.id && badKeywords.some(k => curr.id.toLowerCase().includes(k))) return false;
                if (curr.className && typeof curr.className === 'string' && badKeywords.some(k => curr.className.toLowerCase().includes(k))) return false;
                curr = curr.parentElement;
            }
            return true;
        }

        imgs.forEach(img => {
            if (!img.src || img.src.includes('svg')) return;
            if (!isClean(img)) return;

            const rect = img.getBoundingClientRect();
            
            // 1. Must be in top 1500px (Immediate Product Area)
            if (rect.top > 1500) return;
            
            // 2. Must be VISIBLE
            if (rect.width === 0 || rect.height === 0 || window.getComputedStyle(img).display === 'none') return;
            
            // 3. Must be LARGE (Product images are usually the biggest things in the top fold)
            if (rect.width < 450 || rect.height < 450) return;

            // 4. Center Bias
            // Distance from horizontal center
            const centerX = rect.left + rect.width / 2;
            const deviation = Math.abs(centerX - (viewportWidth / 2));
            
            candidates.push({
                src: img.currentSrc || img.src,
                width: rect.width,
                height: rect.height,
                score: (rect.width * rect.height) - (deviation * 10), // Big & Center = High Score
                rect: rect
            });
        });

        // Sort desc by score
        candidates.sort((a, b) => b.score - a.score);

        // Dedupe
        const unique = new Set();
        return candidates.map(c => c.src).filter(url => {
            if (unique.has(url)) return false;
            unique.add(url);
            return true;
        });
    }''')
    
    if candidates:
        final_list = candidates[:5]
        return final_list, f"Visual: Found {len(final_list)} large images in top viewport."

    return [], "Visual: No prominent images found in top fold."
