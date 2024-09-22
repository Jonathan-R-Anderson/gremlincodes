# Use the official Nginx image as the base image
FROM nginx:alpine

# Install OpenSSL to generate self-signed certificates inside the container
RUN apk add --no-cache openssl

# Create a directory for SSL certificates
RUN mkdir /etc/nginx/ssl

# Generate a self-signed SSL certificate (valid for 365 days)
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/self-signed.key \
    -out /etc/nginx/ssl/self-signed.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=localhost"

# Generate a Diffie-Hellman group for added security
RUN openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048

# Copy the custom Nginx configuration file to the container
COPY nginx.conf /etc/nginx/nginx.conf

# Expose ports for HTTP (80) and HTTPS (443)
EXPOSE 443

# Start Nginx (default command is already provided by the base image)
CMD ["nginx", "-g", "daemon off;", "-c", "/etc/nginx/nginx.conf", "-e", "debug"]