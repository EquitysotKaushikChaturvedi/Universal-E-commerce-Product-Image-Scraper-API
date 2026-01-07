# scraper/agents/ecommerce.py
"""
AGENT 5: E-COMMERCE SPECIALIST (eBay, Amazon, Flipkart)
-------------------------------------------------------
Purpose: Extract high-resolution images from specific giant e-commerce platforms 
that have unique DOM structures not covered by generic structural agents.

Supported:
- eBay (data-zoom-src)
- Amazon (data-old-hires, dynamic-image JSON)
- Flipkart (blob/layout logic)
"""

from playwright.sync_api import Page
import json
import sys

def run_ecommerce_agent(page: Page):
    """
    Returns: (list_of_urls, strategy_note) or ([], "")
    """
    url = page.url.lower()
    
    # === EBAY ===
    if "ebay" in url:
        return run_ebay_logic(page)

    # === AMAZON ===
    if "amazon" in url:
        return run_amazon_logic(page)

    # === FLIPKART ===
    if "flipkart" in url:
        return run_flipkart_logic(page)

    return [], ""

def run_ebay_logic(page: Page):
    # print("[Agent 5] Running eBay logic...", file=sys.stderr)
    
    # eBay often puts high-res zoom link in 'data-zoom-src' on the active image or carousel items
    images = page.evaluate('''() => {
        const candidates = [];
        
        // 1. Check 'ux-image-carousel-item' images (filmstrip/carousel)
        const carouselImgs = document.querySelectorAll('.ux-image-carousel-item img, .ux-image-filmstrip-carousel-item img');
        carouselImgs.forEach(img => {
            if (img.dataset.zoomSrc) candidates.push(img.dataset.zoomSrc);
            else if (img.dataset.src) candidates.push(img.dataset.src);
            else candidates.push(img.src);
        });

        // 2. Check main active image if carousel failed
        if (candidates.length === 0) {
            const mainImg = document.querySelector('.ux-image-carousel-item.active.image img');
            if (mainImg) {
                if (mainImg.dataset.zoomSrc) candidates.push(mainImg.dataset.zoomSrc);
                else candidates.push(mainImg.src);
            }
        }
        
        // 3. Fallback: 'data-zoom-src' anywhere
        if (candidates.length === 0) {
            const allZooms = document.querySelectorAll('img[data-zoom-src]');
            allZooms.forEach(img => candidates.push(img.dataset.zoomSrc));
        }

        // Clean duplicates and small images
        return [...new Set(candidates)].filter(u => u && u.startsWith('http') && !u.includes('s-l64'));
    }''')
    
    # eBay High-Res Hack: Change 's-lXXX' to 's-l1600'
    # Examples: https://i.ebayimg.com/images/g/.../s-l500.jpg -> s-l1600.jpg
    final_images = []
    for img in images:
        if "ebayimg.com" in img:
            import re
            high_res = re.sub(r's-l\d+\.', 's-l1600.', img)
            final_images.append(high_res)
        else:
            final_images.append(img)
            
    if final_images:
        return list(set(final_images)), "Agent 5 (eBay Specialist)"
    return [], ""

def run_amazon_logic(page: Page):
    # print("[Agent 5] Running Amazon logic...", file=sys.stderr)
    
    # Amazon High-Res is usually in 'data-old-hires' or hidden in a JSON object in 'data-a-dynamic-image'
    images = page.evaluate('''() => {
        const candidates = [];
        
        // 1. Landing Image (Main)
        const landing = document.getElementById('landingImage') || document.getElementById('imgBlkFront');
        if (landing) {
            // Priority: Old Hires
            if (landing.dataset.oldHires) candidates.push(landing.dataset.oldHires);
            
            // Priority: Dynamic Image (JSON keys are URLs)
            if (landing.dataset.aDynamicImage) {
                try {
                    const data = JSON.parse(landing.dataset.aDynamicImage);
                    // keys are URLs. Sort by keys? No, keys are URLs. values are [w, h]
                    // We want biggest dimensions.
                    const sorted = Object.entries(data).sort((a,b) => (b[1][0] * b[1][1]) - (a[1][0] * a[1][1]));
                    sorted.forEach(entry => candidates.push(entry[0]));
                } catch(e) {}
            }
        }
        
        // 2. AltImages (thumbnails usually link to main)
        const altImgs = document.querySelectorAll('#altImages ul li img, #imageBlock .a-button-text img');
        altImgs.forEach(img => {
            if (img.src) {
                // Amazon thumbnail hack: Remove resolution token
                // e.g. ..._SS40_.jpg -> .jpg
                // Logic handled in python to stay clean here, or we pass src.
                candidates.push(img.src);
            }
        });

        return [...new Set(candidates)];
    }''')
    
    # Amazon URL Cleaning
    # Remove ._AC_...._.jpg junk to get clean high res
    final_images = []
    import re
    for img in images:
        if "m.media-amazon.com" in img or "images-na.ssl-images-amazon.com" in img:
            # Pattern: https://.../I/71..._AC_SY879_.jpg
            # We want: https://.../I/71....jpg
            
            # 1. Remove strict crop patterns like _AC_..._
            clean = re.sub(r'\._AC_.*?\.(jpg|jpeg|png)', r'.\1', img)
            
            # 2. Remove resolution patterns like _SX450_ or _SY879_
            clean = re.sub(r'\._S[XY]\d+_.*?\.(jpg|jpeg|png)', r'.\1', clean)
            
            # 3. Remove generic resolution
            clean = re.sub(r'\._\w{2,}\.(jpg|jpeg|png)', r'.\1', clean)
            
            final_images.append(clean)
        else:
            final_images.append(img)

    if final_images:
        return list(set(final_images)), "Agent 5 (Amazon Specialist)"
    return [], ""

def run_flipkart_logic(page: Page):
    # print("[Agent 5] Running Flipkart logic...", file=sys.stderr)
    
    # Flipkart uses blobs or specialized cloudfront links
    # Often standard img tags with resolution params in URL
    images = page.evaluate('''() => {
        const candidates = [];
        const imgs = document.querySelectorAll('img._396cs4, img._2r_T1I, img.q6DClP'); // Common flipkart product classes
        
        imgs.forEach(img => {
            if (img.src) candidates.push(img.src);
        });
        
        return [...new Set(candidates)];
    }''')
    
    final_images = []
    import re
    for img in images:
        # Flipkart: http://.../image/128/128/x/y/z.jpg
        # We want: http://.../image/original/original/x/y/z.jpg or massive resolution
        # Usually replace /128/128/ with /832/832/ or similar
        
        if "flixcart.com" in img:
            clean = re.sub(r'/image/\d+/\d+/', '/image/1664/1664/', img) # Max res
            final_images.append(clean)
        else:
            final_images.append(img)
            
    if final_images:
        return list(set(final_images)), "Agent 5 (Flipkart Specialist)"
    return [], ""
