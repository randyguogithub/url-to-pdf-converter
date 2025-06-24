FROM node:18-slim

# Install Chromium dependencies (specific for Debian/Ubuntu based images like node:slim)
# These dependencies are crucial for Puppeteer's Chromium to run correctly in a headless environment.
# This list is updated for modern Debian (like Bookworm, which node:18-slim uses)
# Based on common Puppeteer recommendations and modern Debian package lists.
RUN apt-get update \
    && apt-get install -y \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatspi2.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxrender1 \
    libxtst6 \
    xdg-utils \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /workspace

# Copy package.json and package-lock.json (if exists)
# to take advantage of Docker layer caching
COPY package*.json ./

# Install Node.js dependencies (including puppeteer)
# Use --omit=dev to not install devDependencies in the production image
RUN npm install

# Copy the rest of the application code
COPY . .
RUN ls -all
# Command to run the Node.js script when the container starts
# The args for index.js will be passed via Cloud Build steps as environment variables
CMD ["node", "index.js"]