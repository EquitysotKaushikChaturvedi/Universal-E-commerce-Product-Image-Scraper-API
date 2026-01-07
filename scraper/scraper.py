# scraper/scraper.py
"""
CORE SCRAPER ARBITER (3-AGENT CASCADE)
--------------------------------------
Orchestrates the High-Accuracy Extraction Pipeline.
Updated for AJIO (Firefox Headless Mode - Production Ready).

Pipeline:
1. Firefox Init (Bypasses Chrome Blocking, Headless)
2. Context Extraction (Title, H1)
3. Agent 1: Structural (Strict) -> Judges
4. Agent 2: Context (Smart) -> Judges
5. Agent 3: Visual (Fallback) -> Judges
6. Agent 4: Myntra (Background Img) -> Judges
7. Agent 5: E-commerce (eBay/Amazon) -> Judges
8. Agent 6: Shopify Specialist -> Judges
9. Agent 7K: Elite Extractor (Priority 0) -> Judges
10. Final Output
"""

import sys
import json
import time
import random
from playwright.sync_api import sync_playwright

# Agents
try:
    from agents.structural import run_structural_agent
    from agents.context import run_context_agent
    from agents.visual import run_visual_agent
    from agents.myntra import run_myntra_agent
    from agents.ecommerce import run_ecommerce_agent
    from agents.shopify import run_shopify_agent
    from agents.agent_7k import run_agent_7k
    from judges import final_judgment
except ImportError:
    sys.path.append('scraper')
    from agents.structural import run_structural_agent
    from agents.context import run_context_agent
    from agents.visual import run_visual_agent
    from agents.myntra import run_myntra_agent
    from agents.ecommerce import run_ecommerce_agent
    from agents.shopify import run_shopify_agent
    from agents.agent_7k import run_agent_7k
    from judges import final_judgment

# Config
TOTAL_BUDGET_MS = 60000 

def stabilize_page(page):
    try:
        page.mouse.move(100, 100)
        time.sleep(0.5)
    except:
        pass

def extract_page_context(page):
    return page.evaluate('''() => {
        let h1 = document.querySelector('h1');
        return {
            title: document.title || "",
            h1: h1 ? h1.innerText.trim() : "",
            url: window.location.href
        }
    }''')

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error_code": "MISSING_ARGUMENT", "message": "No URL provided."}))
        sys.exit(1)
        
    target_url = sys.argv[1]
    
    try:
        with sync_playwright() as p:
            # === FIREFOX LAUNCH (HEADLESS) ===
            # Firefox Headless bypasses AJIO rules that block Chrome Headless.
            # This is "Production Ready" (Invisible).
            
            browser = p.firefox.launch(
                headless=True 
            )
            
            context = browser.new_context(viewport=None)
            page = context.new_page()
            
            # Init Response
            response = {
                "source_url": target_url,
                "strategy_used": "None",
                "total_images": 0,
                "product_images": [],
                "note": ""
            }
            
            # Load
            try:
                page.goto(target_url, wait_until='domcontentloaded', timeout=60000)
                time.sleep(5) 
            except Exception as e:
                response["note"] = f"Navigation Failed: {str(e)[:50]}"
                print(json.dumps(response))
                browser.close()
                sys.exit(0)
                
            stabilize_page(page)
            
            # Quick Post-Load Check
            if "Access Denied" in page.title():
                response["note"] = "ACCESS_DENIED_BY_SITE"
                print(json.dumps(response))
                browser.close()
                sys.exit(0)
            
            # === CONTEXT ===
            page_ctx = extract_page_context(page)
            
            final_images = []
            strategy = "None"
            note = "All agents failed."

            # === AGENT PIPELINE ===

            # 0. AGENT-7K (ELITE EXTRACTOR) - HIGH PRIORITY
            candidates, agent_note = run_agent_7k(page)
            if candidates:
                # TRUST AGENT 7K (Enterprise Luxury Mode - Visual Trust)
                final_images = candidates
                strategy = "Agent 7K (Enterprise Luxury)"
                note = agent_note
            
            # 0. SPECIALIST CHECK (Agent 5 - E-commerce Priority)
            # Run FIRST if domain matches to ensure High-Res Specialist logic is used.
            is_ecommerce = any(d in target_url.lower() for d in ['amazon', 'ebay', 'flipkart'])
            if is_ecommerce:
                candidates, agent_note = run_ecommerce_agent(page)
                if candidates:
                    candidates = list(candidates)
                    judged = final_judgment(page_ctx, candidates, "Agent 5")
                    if judged:
                        final_images = judged
                        strategy = "Agent 5 (E-commerce)"
                        note = agent_note

            # 6. SHOPIFY SPECIALIST (Agent 6)
            if not final_images:
                candidates, agent_note = run_shopify_agent(page)
                if candidates:
                    judged = final_judgment(page_ctx, candidates, "Agent 6")
                    if judged:
                        final_images = judged
                        strategy = "Agent 6 (Shopify)"
                        note = agent_note

            # 1. Structural (Agent 1)
            if not final_images:
                candidates, agent_note = run_structural_agent(page)
                if candidates:
                    judged = final_judgment(page_ctx, candidates, "Agent 1")
                    if judged:
                        final_images = judged
                        strategy = "Agent 1 (Structural)"
                        note = agent_note
            
            if not final_images:
                candidates, agent_note = run_context_agent(page)
                if candidates:
                    judged = final_judgment(page_ctx, candidates, "Agent 2")
                    if judged:
                        final_images = judged
                        strategy = "Agent 2 (Context)"
                        note = agent_note
            
            if not final_images:
                candidates, agent_note = run_visual_agent(page)
                if candidates:
                    judged = final_judgment(page_ctx, candidates, "Agent 3")
                    if judged:
                        final_images = judged
                        strategy = "Agent 3 (Visual)"
                        note = agent_note

            # 4. MYNTRA SPECIFIC (Agent 4)
            if not final_images:
                candidates, agent_note = run_myntra_agent(page)
                if candidates:
                    judged = final_judgment(page_ctx, candidates, "Agent 4")
                    if judged:
                        final_images = judged
                        strategy = "Agent 4 (Myntra)"
                        note = agent_note

            # === FINAL OUTPUT ===
            response["strategy_used"] = strategy
            response["total_images"] = len(final_images)
            response["product_images"] = final_images
            response["note"] = note
            
            print(json.dumps(response))
            browser.close()

    except Exception as e:
        print(json.dumps({
            "error_code": "SCRAPER_CRASH", 
            "message": str(e),
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
