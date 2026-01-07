# scraper/agents/structural.py
"""
AGENT 1: STRUCTURAL (STRICT GALLERY FINDER)
-------------------------------------------
Purpose: Find the explicit product gallery using strong DOM signals.
Refined for AJIO / Slick Sliders / Lazy Loading / HIGH RES.
Strategy:
1. Search for known gallery container classes.
2. Check for role="region" with label "gallery".
3. STRICT: If found, extract only from there.
4. If NOT found, return None.
"""

from playwright.sync_api import Page
import time
import sys

# Priority 1: Explicit Gallery Classes/IDs
GALLERY_SELECTORS = [
    # Specific Sites (AJIO)
    '.img-container .rilrtl-lazy-img', 
    '.slick-track', 
    
    # General
    '.product-gallery', '#product-gallery',
    '[data-testid="product-gallery"]',
    '.product-images', '.product-media',
    
    # Libraries
    '.swiper-container', '.swiper-wrapper',
    '.slick-slider',
    '.owl-stage',
    
    # Specific Sites
    '.product__media-gallery',
    '.pdp-gallery',
    '[class*="Gallery"]',
    '[class*="Carousel"]'
]

def run_structural_agent(page: Page):
    """
    Returns: (list_of_urls, strategy_note) or ([], "")
    """
    
    # === SPECIAL AJIO HIGH-RES RESCUE ===
    # AJIO's DOM often has 473w images, but the Source/JSON has 1117w.
    # We strip the DOM search if we find the Gold Standard.
    is_ajio = "ajio.com" in page.url
    if is_ajio:
        # print("[Agent 1] AJIO detected. Component scan for High-Res...", file=sys.stderr)
        ajio_imgs = page.evaluate('''() => {
            const html = document.body.innerHTML;
            // Pattern: https://assets.ajio.com/....-1117Wx1400H-....jpg
            // Handles both assets.ajio and assets-jiocdn if they follow the pattern
            const regex = /https?:\/\/[^"']+-1117Wx1400H-[^"']+\.(jpg|jpeg|webp)/g;
            const matches = html.match(regex);
            return matches ? Array.from(new Set(matches)) : [];
        }''')
        
        if ajio_imgs and len(ajio_imgs) > 0:
            # Filter matches that look like SWATCH or generic
            final_ajio = [u for u in ajio_imgs if "SWATCH" not in u and "loader" not in u]
            if final_ajio:
                return final_ajio, "Structural: AJIO High-Res Regex"

    # === STANDARD STRUCTURAL ANALYSIS ===
    # 1. Try Specific Selectors
    for selector in GALLERY_SELECTORS:
        try:
            target = page.locator(selector).first
            
            if target.is_visible(timeout=500):
                if 'img' not in selector and 'rilrtl' not in selector:
                    count = target.locator('img').count()
                    container_selector = selector
                else:
                    count = page.locator(selector).count()
                    container_selector = selector.split(' ')[0] if ' ' in selector else selector
                    if 'rilrtl' in selector: container_selector = '.slick-track' 
                
                if count > 0:
                    # print(f"[Agent 1] Found gallery candidate: {selector} ({count} imgs)", file=sys.stderr)
                    images = extract_from_container(page, container_selector)
                    if images:
                        return images, f"Structural: {selector}"
        except:
            continue

    # 2. Try Semantic ARIA Roles
    try:
        region = page.locator('section[aria-label*="gallery"], div[aria-label*="gallery"], [role="region"][aria-label*="product images"]').first
        if region.is_visible(timeout=500):
            count = region.locator('img').count()
            if count > 0:
                # print(f"[Agent 1] Found Semantic Region", file=sys.stderr)
                images = extract_from_element_handle(page, region)
                if images:
                    return images, "Structural: Semantic Region"
    except:
        pass

    return [], "No explicit gallery container found."

def extract_from_container(page, selector):
    """
    Extracts high-res images from a specific container selector.
    """
    return page.evaluate(f'''() => {{
        let container = document.querySelector('{selector}');
        if (!container) {{
             container = document.querySelector('.slick-track');
        }}
        if (!container) return [];
        
        const imgs = Array.from(container.querySelectorAll('img'));
        
        return imgs.map(img => {{
             // HIGH RES EXTRACTION
             if (img.dataset.zoomSrc) return img.dataset.zoomSrc;
             if (img.dataset.highRes) return img.dataset.highRes;
             if (img.dataset.original) return img.dataset.original;
             if (img.dataset.full) return img.dataset.full;
             if (img.parentElement && img.parentElement.tagName === 'A' && img.parentElement.href.match(/\.(jpg|jpeg|png|webp)$/i)) {{
                 return img.parentElement.href;
             }}

             let src = img.currentSrc || img.src;
             
             if (img.dataset.src) src = img.dataset.src;
             if (img.dataset.lazy) src = img.dataset.lazy;
             
             if (img.srcset) {{
                 const candidates = img.srcset.split(',').map(s => {{
                     const parts = s.trim().split(/\s+/);
                     const url = parts[0];
                     let width = 0;
                     if (parts.length > 1 && parts[1].endsWith('w')) {{
                         width = parseInt(parts[1]);
                     }}
                     return {{ url, width }};
                 }});
                 candidates.sort((a, b) => b.width - a.width);
                 if (candidates.length > 0) src = candidates[0].url;
             }}
             
             if (img.closest('.related-products')) return null;
             
             const isGallery = container.classList.contains('slick-track') || 
                               container.classList.contains('swiper-wrapper') ||
                               container.id.includes('gallery');
                               
             if (!isGallery && img.naturalWidth < 300) return null; 
             
             return src;
        }}).filter(s => s && s.startsWith('http') && !s.includes('svg'));
    }}''')

def extract_from_element_handle(page, locator):
    """
    Extracts from a playwright locator (semantic region).
    """
    handle = locator.element_handle()
    return handle.evaluate('''el => {
        const imgs = Array.from(el.querySelectorAll('img'));
        return imgs.map(img => {
             if (img.dataset.zoomSrc) return img.dataset.zoomSrc;
             if (img.dataset.original) return img.dataset.original;

             let src = img.src;
             if (img.dataset.src) src = img.dataset.src;
             
             if (img.srcset) {
                 const candidates = img.srcset.split(',').map(s => {
                     const parts = s.trim().split(/\s+/);
                     return { url: parts[0], width: (parts[1] && parts[1].endsWith('w')) ? parseInt(parts[1]) : 0 };
                 });
                 candidates.sort((a, b) => b.width - a.width);
                 if (candidates.length > 0) src = candidates[0].url;
             }
             if (img.naturalWidth < 300) return null;
             return src;
        }).filter(s => s && s.startsWith('http'));
    }''')
