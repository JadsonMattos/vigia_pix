FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy code and build
COPY . .
RUN npm run build

# Production image
FROM node:18-alpine

WORKDIR /app

# Copy only necessary files
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/next.config.js ./

EXPOSE 3000

ENV NODE_ENV=production

CMD ["npm", "start"]


