# Stage 1: Use a Node.js image to build the app
FROM node:18-slim as builder

# Set the working directory
WORKDIR /app

# Copy package.json and the package-lock.json.
# The package-lock.json is essential for `npm ci`.
COPY package.json ./
COPY package-lock.json ./

# Install dependencies using `npm ci` for a clean, fast, and reproducible install.
RUN npm ci

# Copy the rest of the application source code
COPY . .

# Stage 2: Create the final, lean image
# Use an official Puppeteer image which includes all necessary system dependencies for Chromium.
FROM ghcr.io/puppeteer/puppeteer:22.15.0

# Cloud Build uses /workspace by default, so we'll use it for consistency.
WORKDIR /workspace

# Copy node_modules and application code from the builder stage
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/index.js ./index.js

# Define the default command to run when the container starts.
CMD ["node", "index.js"]