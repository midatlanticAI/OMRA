#!/bin/sh
set -e

# Replace environment variables in nginx.conf
API_URL=${VITE_API_URL:-http://localhost:8000/api}
sed -i "s|\${API_URL}|$API_URL|g" /etc/nginx/conf.d/default.conf

# Start nginx
exec nginx -g "daemon off;" 