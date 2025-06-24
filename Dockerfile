# Dockerfile
# Use a slim Node.js base image
FROM node:18-slim

# Install Chromium dependencies (specific for Debian/Ubuntu based images like node:slim)
# These dependencies are crucial for Puppeteer's Chromium to run correctly in a headless environment.
# List from Puppeteer's troubleshooting guide: https://pptr.dev/#?product=Puppeteer&version=v22.0.0&show=usage-running-puppeteer-in-docker
RUN apt-get update \
    && apt-get install -y \
    gconf-service \
    libasound2 \
    libatk1.0-0 \
    libcairo2 \
    libcups2 \
    libfontconfig1 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libjpeg-turbo8 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    ca-certificates \
    fonts-liberation \
    libappindicator1 \
    libnss3-tools \
    lsb-release \
    xdg-utils \
    wget \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json (if exists)
# to take advantage of Docker layer caching
COPY package*.json ./

# Install Node.js dependencies (including puppeteer)
# Use --omit=dev to not install devDependencies in the production image
RUN npm install --omit=dev

# Copy the rest of the application code
COPY . .

# Command to run the Node.js script when the container starts
# The args for index.js will be passed via Cloud Build steps as environment variables
CMD ["node", "index.js"]
