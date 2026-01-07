# scraper/agents/shopify.py
"""
AGENT 6: SHOPIFY SPECIALIST
---------------------------
Purpose: Extract images from Shopify-powered websites.
Triggers: Runs if 'myshopify.com' is in source or common Shopify classes are found.

Logic:
1. Search for `window.Shopify` objects.
2. Search for `<script id="ProductJson-...">` or similar JSON blobs.
3. Fallback: Search for `.product-single__photo` or `.product__media-item`.
4. Maximize resolution (Shopify CDN links usually have `_1024x1024` or similar, we want `master` or strip resolution).
"""

from playwright.sync_api import Page
import json
import re
import sys

def run_shopify_agent(page: Page):
    """
    Returns: (list_of_urls, strategy_note) or ([], "")
    """
    # 1. Detection: Is this Shopify?
    # We can check global variable window.Shopify
    is_shopify = page.evaluate("!!window.Shopify")
    
    if not is_shopify:
        # Check source for cdn.shopify.com
        content = page.content()
        if "cdn.shopify.com" not in content and "myshopify" not in content:
            return [], "" # Not Shopify
            
    # print("[Agent 6] Running Shopify logic...", file=sys.stderr)

    # 2. STRATEGY A: Product JSON (Gold Standard)
    # Most Shopify themes dump the full product data in a JSON script tag.
    # Look for ids like ProductJson-..., product-json, or just search all script tags for a structure.
    
    images_from_json = page.evaluate('''() => {
        const candidates = [];
        
        // Try to find product json
        const scripts = Array.from(document.querySelectorAll('script[type="application/json"]'));
        for (const s of scripts) {
            try {
                if (s.id.toLowerCase().includes('product') || s.innerText.includes('"images":')) {
                    const data = JSON.parse(s.innerText);
                    // Check standard Shopify Product JSON structure
                    if (data.images && Array.isArray(data.images)) {
                        data.images.forEach(img => {
                             // img can be string or object
                             if (typeof img === 'string') candidates.push(img);
                             else if (img.src) candidates.push(img.src);
                        });
                    }
                    if (data.media && Array.isArray(data.media)) {
                        data.media.forEach(m => {
                            if (m.preview_image && m.preview_image.src) candidates.push(m.preview_image.src);
                            else if (m.src) candidates.push(m.src);
                        });
                    }
                }
            } catch(e) {}
        }
        
        // Try Meta object
        if (window.meta && window.meta.product && window.meta.product.images) {
             window.meta.product.images.forEach(img => candidates.push(img));
        }

        return candidates;
    }''')
    
    if images_from_json:
        return clean_shopify_urls(images_from_json), "Agent 6 (Shopify JSON)"

    # 3. STRATEGY B: DOM Extraction (Specific Classes)
    # Common Shopify classes
    dom_images = page.evaluate('''() => {
        const candidates = [];
        const selectors = [
            '.product-single__photo', 
            '.product__media-item img', 
            '.product-gallery__image',
            '.grid__item .product-card__image',
            '[data-product-single-thumbnail]'
        ];
        
        selectors.forEach(sel => {
            document.querySelectorAll(sel).forEach(img => {
                if (img.dataset.src) candidates.push(img.dataset.src);
                else if (img.srcset) {
                     // Get last item in srcset (usually largest)
                     const parts = img.srcset.split(',');
                     const last = parts[parts.length-1].trim().split(' ')[0];
                     candidates.push(last);
                }
                else if (img.src) candidates.push(img.src);
            });
        });
        
        return [...new Set(candidates)];
    }''')
    
    if dom_images:
        return clean_shopify_urls(dom_images), "Agent 6 (Shopify DOM)"

    return [], ""

def clean_shopify_urls(urls):
    clean = []
    for u in urls:
        if not u: continue
        # Handle protocol-relative //cdn.shopify...
        if u.startswith('//'):
            u = 'https:' + u
            
        # Shopify High-Res Logic:
        # URL often: .../products/my-image_small.jpg?v=...
        # We want: .../products/my-image.jpg (Master) or .../products/my-image_2048x2048.jpg
        # Safest is to remove the size suffix _100x100, _small, _large, etc. BUT keep the ID/Name.
        # Actually in Shopify, removing the underscore-size usually gives original.
        
        # Regex to strip size params like _1024x1024 or _large
        # Pattern match: (_[0-9]+x[0-9]+)|(_small)|(_medium)|(_large)|(_compact) 
        # occurring before the extension.
        
        # Simple cleanup: remove everything after ?v= (version) to keep it clean? No, version is fine.
        # Remove size:
        
        new_u = re.sub(r'(_\d+x\d+)|(_small)|(_medium)|(_large)|(_compact)|(_grande)', '', u)
        
        clean.append(new_u)
        
    return list(dict.fromkeys(clean)) # unique
