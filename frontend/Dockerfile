# --- Development Stage ---
FROM node:22-slim AS development

WORKDIR /app

# Install curl for healthcheck + update npm
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

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

# Install curl + update npm
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends curl python3 make g++ \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g npm@latest

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source and build
COPY . .
ARG NUXT_PUBLIC_API_BASE=http://backend:8000/api/v1
ENV NUXT_PUBLIC_API_BASE=$NUXT_PUBLIC_API_BASE
RUN npm run build


# --- Runner (Production) Stage ---
FROM node:22-slim AS runner

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

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
