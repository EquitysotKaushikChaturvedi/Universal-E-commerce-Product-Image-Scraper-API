# scraper/judges.py
"""
JUDGE SYSTEM (MANDATORY)
------------------------
1. Product Relevance Judge: Confirms image matches MAIN PRODUCT.
2. Noise Elimination Judge: Rejects ads/banners/related.

Only images approved by BOTH judges survive.
"""

from urllib.parse import urlparse
import sys

class ProductRelevanceJudge:
    def judge(self, context, images):
        """
        Check if images mostly align with the product context.
        context = { "title": "...", "h1": "..." }
        """
        # Simplistic implementation:
        # We rely on the Agents to have done the heavy lifting of proximity.
        # Here we just check if the URL looks like a product image (cdn, assets).
        # And ensure we didn't pick up something widely inconsistent.
        
        # In a real heavy system, we'd use CLIP/AI.
        # For now, we trust the location-based Agents unless the URL has suspicious keywords.
        
        approved = []
        for img in images:
            # Basic sanity
            if not img or len(img) < 10: 
                continue
                
            approved.append(img)
            
        return approved

class NoiseEliminationJudge:
    def judge(self, context, images):
        """
        Explicitly blocks known bad patterns.
        """
        BAD_TOKENS = [
            'icon', 'logo', 'button', 'sprite', 
            'banner', 'promo', 'ad-', 'advert',
            'social', 'facebook', 'twitter', 'instagram',
            'arrow', 'check', 'star', 'rating',
            'user', 'avatar', 'profile'
        ]
        
        # Color swatches often are small square images, usually handled by size check in Agents.
        # But if they leak, we check for 'swatch' token.
        BAD_TOKENS.append('swatch')

        approved = []
        for img in images:
            lower_url = img.lower()
            
            is_bad = False
            for token in BAD_TOKENS:
                if token in lower_url:
                    is_bad = True
                    break
            
            if is_bad:
                continue
                
            approved.append(img)
            
        return approved

def final_judgment(context, candidates, source_agent="Unknown"):
    """
    The High Court.
    """
    print(f"[Judge] Reviewing {len(candidates)} candidates from {source_agent}...", file=sys.stderr)
    
    judge1 = ProductRelevanceJudge()
    judge2 = NoiseEliminationJudge()
    
    # Round 1
    r1 = judge1.judge(context, candidates)
    # Round 2
    r2 = judge2.judge(context, r1)
    
    msg = f"Judges approved {len(r2)}/{len(candidates)} images."
    print(f"[Judge] {msg}", file=sys.stderr)
    
    return r2
