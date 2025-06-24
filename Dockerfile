# Stage 1: Use a Node.js image to build the app
FROM node:18-slim as builder

# Set the working directory
WORKDIR /app

# Install pnpm, as it's used for local development.
RUN npm install -g pnpm

# Copy package manifests. Make sure pnpm-lock.yaml is committed to your repository.
COPY package*.json ./
COPY pnpm-lock.yaml ./

# Install dependencies using pnpm. --frozen-lockfile is the equivalent of `npm ci`.
RUN pnpm install --frozen-lockfile

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