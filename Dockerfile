FROM python:3.9-slim

# ENSURE LOGS SHOW UP IN RENDER
ENV PYTHONUNBUFFERED=1

# Install Node.js
RUN apt-get update && apt-get install -y nodejs npm

# Install Python Dependencies & Playwright
WORKDIR /app
COPY . .
RUN pip install -r scraper/requirements.txt

# INSTALL FIREFOX (Critical for Agent 7K / AJIO)
# The scraper uses Firefox Headless to bypass blocking.
RUN playwright install firefox
RUN playwright install-deps firefox

# Install Node Dependencies
RUN npm install

# Start Server
CMD ["npm", "start"]
