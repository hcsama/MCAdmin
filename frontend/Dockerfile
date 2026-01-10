# Stage 1: Build
FROM node:20-slim AS builder

WORKDIR /app

# Copy configuration and dependency lists
COPY package.json svelte.config.js tsconfig.json vite.config.ts ./

# Install dependencies (including devDependencies for build)
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build
RUN npm prune --omit=dev --ignore-scripts

# Stage 2: Production
FROM node:20-slim

WORKDIR /app

# Copy built application
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules

# Set production environment
ENV NODE_ENV=production

EXPOSE 3000

# adapter-node builds into 'build/' by default
CMD ["node", "build"]
