# Build stage
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --silent

# Copy project files
COPY . .

# Create .env file from environment variables or use default
RUN touch .env && \
    echo "VITE_API_URL=${VITE_API_URL:-http://localhost:8000/api}" >> .env && \
    echo "VITE_AUTH_STORAGE_KEY=${VITE_AUTH_STORAGE_KEY:-openmanus-auth}" >> .env && \
    echo "VITE_APP_VERSION=${VITE_APP_VERSION:-0.1.0}" >> .env

# Build the application
RUN npm run build

# Production stage
FROM nginx:stable-alpine

# Set working directory
WORKDIR /usr/share/nginx/html

# Copy built assets from build stage
COPY --from=build /app/dist .

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Add security headers
RUN echo 'add_header X-Frame-Options "DENY";' >> /etc/nginx/conf.d/default.conf && \
    echo 'add_header X-Content-Type-Options "nosniff";' >> /etc/nginx/conf.d/default.conf && \
    echo 'add_header X-XSS-Protection "1; mode=block";' >> /etc/nginx/conf.d/default.conf && \
    echo 'add_header Content-Security-Policy "default-src \'self\'; script-src \'self\'; object-src \'none\'; img-src \'self\' data:; style-src \'self\' \'unsafe-inline\'; font-src \'self\' fonts.googleapis.com fonts.gstatic.com; connect-src \'self\' ${VITE_API_URL:-http://localhost:8000/api}";' >> /etc/nginx/conf.d/default.conf && \
    echo 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";' >> /etc/nginx/conf.d/default.conf

# Run with non-root user for security
RUN addgroup -g 1001 -S appuser && \
    adduser -u 1001 -S appuser -G appuser && \
    chown -R appuser:appuser /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html && \
    chmod -R 755 /var/cache/nginx && \
    chmod -R 755 /var/run && \
    touch /var/run/nginx.pid && \
    chmod 755 /var/run/nginx.pid

USER appuser

# Copy shell script to handle environment variables at runtime
COPY --chown=appuser:appuser scripts/entrypoint.sh /
RUN chmod +x /entrypoint.sh

# Start Nginx server
ENTRYPOINT ["/entrypoint.sh"] 