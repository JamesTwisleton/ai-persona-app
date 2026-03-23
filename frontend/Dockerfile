# ============================================================================
# Development stage
# ============================================================================
FROM node:20-alpine AS development

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]

# ============================================================================
# Build stage
# ============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Bake the API URL in at build time (Next.js NEXT_PUBLIC_* vars are build-time)
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN npm run build

# ============================================================================
# Production stage
# ============================================================================
FROM node:20-alpine AS production

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY --from=builder /app/.next ./.next

EXPOSE 3000
CMD ["npm", "start"]
