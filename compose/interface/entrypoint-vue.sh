# Create NGINX config using environment variables
envsubst < /app/nginx.conf.template > /app/nginx.conf

# Run nginx to serve vue app
nginx -c /app/nginx.conf
