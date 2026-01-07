# scraper/agents/agent_7k.py
"""
AGENT-7K: ENTERPRISE-GRADE LUXURY IMAGE EXTRACTOR (GOD MODE)
------------------------------------------------------------
MISSION: Extract products from High-Security, Luxury, and Headless sites.
TRUST MODEL: Visual-Only (Level 1). No hidden data. No guessing.
PLATFORMS: Louis Vuitton, Nike, Adidas, H&M, Zara, Amazon, Myntra.

STRATEGIES:
1. Visual Hero Lock-on (Level 2)
2. Background Style Harvest (Level 3)
3. Safe Shadow DOM Traversal (Level 4)
4. Safe High-Res Normalization (Level 5)
5. Strict Luxury Filtering (Level 7)
"""

from playwright.sync_api import Page
import re
import urllib.parse
import sys

NAME = "AGENT-7K"

def run_agent_7k(page: Page):
    """
    EXECUTING AGENT-7K V3 (ENTERPRISE LUXURY)
    """
    
    # === STRATEGY: VISUAL HERO LOCK-ON (JS) ===
    # Scans for the "Hero" product image that is visible to a human.
    
    visual_payload = '''() => {
        const CANDIDATES = [];
        const SEEN = new Set();
        const MIN_SIZE = 450; // Strict Luxury Requirement (Level 7)
        const VIEWPORT_LIMIT = 2000; // Limit scan to top area (Level 2)
        
        // Helper: Is Visible?
        const isVisible = (el) => {
            if (!el) return false;
            const style = window.getComputedStyle(el);
            if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return false;
            const rect = el.getBoundingClientRect();
            // Must be in top viewport and have size
            return rect.width > 0 && rect.height > 0 && rect.top < VIEWPORT_LIMIT && rect.bottom > 0;
        };

        // Helper: Get Shadow Roots (Level 4 - Safe Open Mode Only)
        const getAllShadows = (root) => {
            const all = [];
            try {
                const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);
                while(walker.nextNode()) {
                    const node = walker.currentNode;
                    if (node.shadowRoot) {
                        all.push(node.shadowRoot);
                        all.push(...getAllShadows(node.shadowRoot));
                    }
                }
            } catch(e) {}
            return all;
        };
        
        // Helper: Add Candidate
        const add = (url, score, type) => {
            if (!url) return;
            if (url.startsWith('data:')) return; 
            if (SEEN.has(url)) return;
            
            SEEN.add(url);
            CANDIDATES.push({ url, score, type });
        };

        // 1. SCAN VISIBLE DOM (Document + Open Shadows)
        const roots = [document, ...getAllShadows(document.body)];
        const centerX = window.innerWidth / 2;
        
        roots.forEach(root => {
            // A. IMG TAGS
            root.querySelectorAll('img').forEach(img => {
                if (!isVisible(img)) return;
                
                const rect = img.getBoundingClientRect();
                
                // Strict Size Filter
                const w = img.naturalWidth || rect.width;
                const h = img.naturalHeight || rect.height;
                if (w < MIN_SIZE && h < MIN_SIZE) return; 

                // Scoring: Hero Lock-on (Level 2)
                const area = rect.width * rect.height;
                const distFromCenter = Math.abs((rect.left + rect.width / 2) - centerX);
                const visualProminence = area / (distFromCenter + 1); 
                
                // Boost keywords
                let score = visualProminence;
                const idClass = (img.id + img.className || "").toLowerCase();
                if (idClass.includes('main') || idClass.includes('hero') || idClass.includes('product')) {
                    score *= 2.0;
                }

                // Source Selection
                let src = img.getAttribute('data-zoom-image') || 
                          img.getAttribute('data-zoom-src') || 
                          img.currentSrc || 
                          img.src;
                
                // Handle srcset locally if possible to get best fit
                if (img.srcset) {
                     const parts = img.srcset.split(',');
                     // simple logic: take last one
                     src = parts[parts.length - 1].trim().split(' ')[0];
                }
                
                // Resolve relative URLs (Critical for LV)
                if (src) {
                    try {
                        src = new URL(src, document.baseURI).href;
                    } catch(e) {}
                }

                add(src, score, 'img');
            });

            // B. BACKGROUND IMAGES (Level 3)
            // Critical for luxury sites that use div backgrounds
            root.querySelectorAll('*').forEach(el => {
                if (!isVisible(el)) return;
                const style = window.getComputedStyle(el);
                const bg = style.backgroundImage;
                
                if (bg && bg.startsWith('url(')) {
                    const rect = el.getBoundingClientRect();
                    // Must be substantial size
                    if (rect.width < MIN_SIZE && rect.height < MIN_SIZE) return;
                    
                    const match = bg.match(/url\\(['"]?(.*?)['"]?\\)/);
                    if (match && match[1]) {
                         let bgUrl = match[1];
                         try {
                             bgUrl = new URL(bgUrl, document.baseURI).href;
                         } catch(e) {}
                         add(bgUrl, rect.width * rect.height * 0.8, 'bg');
                    }
                }
            });
        });
        
        // Return strictly sorted by Visual Score
        return CANDIDATES.sort((a, b) => b.score - a.score).map(c => ({ src: c.url, method: `js_visual_${c.type}` }));
    }'''

    try:
        # Run Visual Engine
        js_candidates = page.evaluate(visual_payload)
        candidates.extend(js_candidates)

        # ------------------------------------------------------------------
        # STRATEGY 4: H&M / ZARA / UNIQLO SPECIFIC (The "Scroll & Harvest" Maneuver)
        # ------------------------------------------------------------------
        # H&M specifically lazy loads heavily. We must force scroll.
        if "hm.com" in page.url or "zara.com" in page.url or "uniqlo.com" in page.url:
            print(f"[{NAME}] Detected Fashion Giant. Initiating deep scroll...", file=sys.stderr)
            try:
                # Scroll down repeatedly to trigger lazy loading
                for _ in range(5):
                    page.evaluate("window.scrollBy(0, 800)")
                    page.wait_for_timeout(500)
                
                # H&M Specific: Click "Load more" if present (often in gallery)
                try:
                    page.click('button:has-text("Load more")', timeout=1000)
                except:
                    pass
                    
                # Specific selectors for H&M's new gallery structure
                hm_selectors = [
                    ".product-detail-main-image-container img",
                    ".product-detail-thumbnails img",
                    ".product-gallery img",
                    "figure.pdp-image-template img",
                    ".product-detail-images img"
                ]
                for sel in hm_selectors:
                    elements = page.query_selector_all(sel)
                    for el in elements:
                        src = el.get_attribute('src')
                        if src:
                            candidates.append({'src': src, 'method': 'hm_special_dom'})
                            
            except Exception as e:
                print(f"[{NAME}] Scroll maneuver errors: {e}", file=sys.stderr)

        # ------------------------------------------------------------------
        # STRATEGY 6: AMAZON / FLIPKART RETRY (The "Double Tap")
        # ------------------------------------------------------------------
        # Only retry if initial visual scan yielded few results
        if ("amazon" in page.url or "flipkart" in page.url) and len(candidates) < 2:
            print(f"[{NAME}] Low yield on Retail Giant. Attempting Reload & Retry...", file=sys.stderr)
            try:
                page.reload(wait_until="domcontentloaded")
                page.wait_for_timeout(2000) # Give it a moment
                # Quick re-scan for common Amazon/Flipkart selectors
                imgs = page.query_selector_all("#landingImage, #imgTagWrapperId img, .a-dynamic-image")
                for i in imgs:
                    src = i.get_attribute('src') or i.get_attribute('data-old-hires')
                    if src: candidates.append({'src': src, 'method': 'amazon_retry'})
            except Exception as e:
                 print(f"[{NAME}] Amazon/Flipkart retry error: {e}", file=sys.stderr)

        # === LEVEL 5 & 7: SAFE NORMALIZATION & STRICT FILTERING ===
        final_urls = process_luxury_images(candidates, page.url)
        
        if final_urls:
            return final_urls, "Agent 7K (Enterprise Luxury)"
        
    except Exception as e:
        print(f"[{NAME}] Error in run_agent_7k: {e}", file=sys.stderr)

    return [], ""

def process_luxury_images(candidates, base_url):
    """
    Normalizes images SAFELY and applies STRICT luxury filtering.
    """
    clean_list = []
    seen = set()
    
    # EXPANDED JUNK TERMS (STRICT FILTER LEVEL 7)
    JUNK_TERMS = [
        'base64', 'icon', 'logo', 'button', 'star', 'rating', 'avatar', 
        'sprite', 'blank', 'transparent', 'gif', 'loader', 'spinner',
        'cookielaw', 'tracking', 'pixel', 'facebook', 'twitter', 
        'instagram', 'pinterest', 'banner', 'campaign', 'editorial',
        'social', 'thumb', 'profile', 'promo', 'advert', 'flag', 'review',
        'arrow', 'chevron', 'plus', 'minus', 'zoom', 'close', 'cookie',
        'footer', 'header', 'cart', 'bag', 'wishlist', 'search', 'menu',
        'share', 'print', 'download', 'play', 'pause', 'video', 'audio',
        'placeholder', 'default', 'empty', 'no-image', 'missing', 'broken'
    ]
    
    # TERMS INDICATING SIGNED/SECURE URLS (DO NOT TOUCH)
    SECURITY_PARAMS = ['sig', 'signature', 'token', 'auth', 'key', 'hmac', 'expires', 'timestamp']

    for c in candidates:
        u = c.get('src')
        if not u: continue
        u = u.strip()
        
        # 1. Normalize protocol-relative URLs
        if u.startswith('//'):
            u = 'https:' + u
            
        # 2. Resolve relative paths (starts with /) using base URL
        if u.startswith('/'):
            try:
                u = urllib.parse.urljoin(base_url, u)
            except Exception:
                continue # Skip if cannot resolve securely

        lower_u = u.lower()
        
        # 3. Strict Junk Filter
        if any(j in lower_u for j in JUNK_TERMS):
            continue
            
        # 4. Extension Check
        if any(u.endswith(ext) for ext in ['.svg', '.ico', '.gif']):
            continue

        # 5. SAFE Normalization (Level 5)
        # Check if URL is signed/sensitive
        is_sensitive = any(p in lower_u for p in SECURITY_PARAMS)
        
        if not is_sensitive:
            # Safe to Normalize
            
            # Amazon
            if 'amazon.' in lower_u or 'media-amazon.com' in lower_u:
                u = re.sub(r'\._S[A-Z0-9]+_\.', '.', u)
            
            # Myntra (Visual extraction is usually good, but just in case)
            if 'assets.myntassets.com' in lower_u:
                 # Ensure http/https
                 pass
                 
            # Flipkart safe upscale
            if 'rukminim1.flixcart.com' in lower_u:
                u = re.sub(r'/image/\d+/\d+/', '/image/1080/1080/', u)
            
            # Shopify safe cleanup
            if 'cdn.shopify.com' in lower_u:
                u = re.sub(r'_(\d+x\d+|small|medium|large|grande|compact|crop_center)(\.[a-zA-Z0-9]+)', r'\2', u)
                u = re.sub(r'\?v=\d+', '', u)
                
            # H&M
            if 'hm.com' in lower_u:
                u = re.sub(r'\?imwidth=\d+', '', u)
                
            # Zara
            if 'zara.' in lower_u:
                 u = re.sub(r'[?&]w=\d+', '', u)
        
        else:
            # SENSITIVE URL DETECTED: KEEP ORIGINAL
            # Do NOT strip params, do NOT change anything.
            pass

        if u not in seen and u.startswith('http'):
            clean_list.append(u)
            seen.add(u)
            
    return clean_list
