# Deployment Guide: Universal Product Scraper

## 🚀 Overview
This project uses **Node.js (Express)** for the backend/frontend and **Python (Playwright)** for the scraping engine. Because it requires a **Full Browser Engine (Chromium)**, deployment requires a platform that supports Docker or heavy runtime dependencies.

---

## Option 1: Render / Railway (RECOMMENDED) ✅
These platforms support Docker/Buildpacks and are compatible with Playwright.

### Steps for Render.com
1.  Push this code to **GitHub**.
2.  Go to [Render.com](https://render.com) -> New **Web Service**.
3.  Connect your GitHub repository.
4.  **CRITICAL STEP**: Under "Runtime", select **Docker**.
    *   *Do NOT select Node or Python.*
    *   *If you do not see "Docker", you might need to create a new service.*
    *   *The file path in logs should be `/app/...`. If it says `/opt/render/...`, you are NOT using Docker.*
5.  **Build Command**: (Leave empty, Docker handles it)
6.  **Start Command**: (Leave empty, Docker handles it)
7.  Deploy!

### Steps for Railway.app
1.  Connect GitHub repo to Railway.
2.  Add a `Dockerfile` (see below) to your repo.
3.  Railway automatically builds and deploys.

---

## Option 2: Vercel (WARNING) ⚠️
**Vercel is NOT recommended** for this specific scraper because:
1.  **Serverless Limits**: Vercel functions have a 50MB size limit. Playwright opens a real browser which exceeds this.
2.  **Timeout Limits**: Vercel "Hobby" plan times out after 10 seconds. Scraping usually takes 15-30 seconds.

### If you MUST use Vercel:
You cannot host the *Scraper/Python* part on Vercel easily.
**Architecture Solution**:
1.  Host the **Frontend** (`public/` + `api/`) on Vercel.
2.  Host the **Scraper Engine** (Python) on a separate VPS or Cloud Run.
3.  Update `api/routes.js` to call your external Scraper endpoint.

---

## Dockerfile (Included)
I have already created a `Dockerfile` in the root directory for you. It is configured to install **Firefox** (required for Agent 7K) instead of Chromium.

If you need to create it manually, here is the content:

```dockerfile
FROM python:3.9-slim

# Install Node.js
RUN apt-get update && apt-get install -y nodejs npm

# Install Python Dependencies & Playwright
WORKDIR /app
COPY . .
RUN pip install -r scraper/requirements.txt

# INSTALL FIREFOX
RUN playwright install firefox
RUN playwright install-deps firefox

# Install Node Dependencies
RUN npm install

# Start Server
CMD ["npm", "start"]
```

## Security & Features
This scraper includes **Agent 7K (Enterprise Luxury Mode)** which features:
*   **Visual-Only Trust**: Crosses Cloudflare/Akamai by acting like a human.
*   **Hero Lock-oon**: Finds main product image visually.
*   **Safe Normalization**: Works on Amazon, H&M, Zara, Myntra, Luxury brands.
*   **Shadow DOM**: Penetrates modern protected sites.
