# Universal E-commerce Product Image Scraper API

## Overview
This project is a sophisticated web scraping API designed to extract high-resolution product images from complex e-commerce platforms. It is specifically optimized for sites with heavy anti-bot protections (WAFs) and dynamic content loading, such as AJIO, Skims, Myntra, and Puma.

The system uses a multi-layered extraction architecture ("Three-Agent Cascade") and employs Headless Firefox to bypass fingerprinting restrictions on sites like AJIO.

## Key Technical Features

### Multi-Agent Architecture
The scraper operates using three distinct agents that run in a specific fallback sequence. Each agent utilizes a unique strategy to identify product images.

1.  **Agent 1: Structural (Strict)**
    *   **Logic**: Searches for known, explicit gallery containers in the DOM (e.g., Slick Slider, Swiper, specific CSS classes like `product-gallery`).
    *   **High-Resolution Extraction**: For specific platforms (like AJIO), this agent bypasses the DOM's low-quality thumbnails by scanning the raw page source code for high-resolution format patterns (e.g., `1117Wx1400H`).
    *   **Behavior**: If this agent finds images, the process terminates successfully. It is the most accurate and preferred method.

2.  **Agent 2: Context (Smart)**
    *   **Logic**: If Agent 1 fails, this agent analyzes the visual hierarchy of the page relative to the Product Title (H1 tag).
    *   **Scoring**: It calculates a relevance score for every image based on vertical proximity to the title, container purity (absence of text/buttons), and aspect ratio.
    *   **Behavior**: Selects the highest-scoring cluster of images.

3.  **Agent 3: Visual (Fallback)**
    *   **Logic**: A fail-safe agent that assumes the product images are the largest, centrally aligned visual elements in the viewport.
    *   **Behavior**: Filters out small icons, banners, and off-screen elements to find the main display image.

4.  **Agent 4: Myntra (Background Img)**
    *   **Logic**: Specialized for Myntra's CSS background-image structure.
    *   **High-Resolution**: Automatically converts `h_720` to `h_1440` (HD).

5.  **Agent 5: E-commerce Specialist (eBay/Amazon/Flipkart)**
    *   **Logic**: Prioritized agent for giant platforms. Runs FIRST for these domains.
    *   **Features**:
        *   **eBay**: Extracts `data-zoom-src` and converts `s-lXXX` URLs to `s-l1600` (Max Res).
        *   **Amazon**: Checks `data-old-hires` and specific dynamic image JSON blobs.
        *   **Flipkart**: Maximizes image URL resolution parameters.

6.  **Agent 6: Shopify Specialist**
    *   **Logic**: Targets Shopify-powered stores (`myshopify` URLs).
    *   **Features**: Extractions via `window.Shopify` or `ProductJson` blobs to get the complete, original-quality image list (1024x1024+).

7.  **Agent 7K: Enterprise Luxury (Priority 0)**
    *   **Logic**: Visual-First "God Mode" (Level 1). Scans visible DOM for Hero images.
    *   **Intelligence**: 
        1. **Hero Lock-On**: Prioritizes large, center-aligned images in the viewport.
        2. **Visual Trust**: Ignores hidden data/network/tokens.
        3. **Safe Normalization**: Detects signed URLs and preserves signatures.
        4. **Shadow DOM**: Penetrates open shadow roots.
        5. **Strict Filter**: Minimum size 450px, strict junk/logo filtering.
    *   **Platforms**: Universal (Luxury, Enterprise, Headless).

### Quality Assurance (Judges)
Every extracted image passes through two validation layers before being returned:
*   **Product Identity Judge**: Ensures the image belongs to the main product and not a "Recommended Product" or "Customer Review."
*   **Noise Elimination Judge**: Rejects banners, icons, placeholder graphics, and low-resolution thumbnails.

### Anti-Bot Evasion (AJIO Optimization)
*   **Engine**: The scraper uses a Playwright-managed **Firefox** instance in Headless mode. This specific configuration is proven to bypass the Akamai/Cloudflare headers used by AJIO, whereas Chromium-based scrapers (puppeteer, chrome) are blocked.
*   **Source Scrum**: To overcome low-resolution lazy-loading issues, the system performs a specific regex scan on the `document.body.innerHTML` to locate high-fidelity image assets that are not yet rendered in the DOM.

--

## Installation

1.  **Prerequisites**:
    *   Node.js (v16+)
    *   Python (v3.10+)

2.  **Install Node Dependencies**:
    ```bash
    npm install
    ```

3.  **Install Python Dependencies & Browsers**:
    ```bash
    cd scraper
    pip install -r requirements.txt
    playwright install firefox
    cd ..
    ```

--

## Usage

### Starting the API Server
To run the application in production mode:

```bash
npm start
```

The server will initialize on port **3000**.

### API Reference

**Endpoint**: `POST /api/scrape`

**Request Body**:
```json
{
  "url": "https://www.ajio.com/product-url-here"
}
```

**Response**:
```json
{
  "source_url": "https://www.ajio.com/product-url-here",
  "strategy_used": "Agent 1 (Structural)",
  "total_images": 5,
  "product_images": [
    "https://assets.ajio.com/.../high-res-image-1.jpg",
    "https://assets.ajio.com/.../high-res-image-2.jpg"
  ],
  "note": "Structural: AJIO High-Res Regex"
}
```

--

## Troubleshooting

*   **EADDRINUSE Error**: If `npm start` fails saying the port is in use, terminate the existing node process (or any process on port 3000) and try again.
*   **Access Denied**: Ensure you have installed the Firefox browser binaries (`playwright install firefox`). The system relies on this specific browser engine to bypass access blocks.
