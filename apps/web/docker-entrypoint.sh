#!/bin/sh
set -e
export PORT="${PORT:-80}"
export API_UPSTREAM="${API_UPSTREAM:-http://localhost:8000}"
envsubst '${PORT} ${API_UPSTREAM}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf
exec nginx -g 'daemon off;'
