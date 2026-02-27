# --- Development Stage ---
FROM node:22-slim AS development

WORKDIR /app

# Update npm to latest to suppress upgrade notice
RUN npm install -g npm@latest

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source
COPY . .

# Standard Nuxt 3 dev environment variables
ENV NODE_ENV=development
ENV HOST=0.0.0.0
ENV PORT=3000

EXPOSE 3000

CMD ["npm", "run", "dev"]


# --- Build Stage ---
FROM node:22-slim AS builder

WORKDIR /app

# Update npm to latest
RUN npm install -g npm@latest

# Install build dependencies (for some npm packages that need them)
RUN apt-get update && apt-get install -y \
    python3 \
    make \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source and build
COPY . .
RUN npm run build


# --- Runner (Production) Stage ---
FROM node:22-slim AS runner

WORKDIR /app

# Security: Add a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

# Copy only the output from builder
COPY --from=builder /app/.output /app/.output

# Standard Nuxt 3 environment variables
ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=3000

EXPOSE 3000

# Start the server
CMD ["node", ".output/server/index.mjs"]
