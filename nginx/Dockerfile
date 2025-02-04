# Use Debian-based slim image
FROM debian:bullseye-slim

# Install required packages, including Nginx and the RTMP module
RUN apt update && apt install -y \
    nginx \
    libnginx-mod-rtmp \
    openssl \
    libssl-dev \
    curl \
    build-essential \
    git \
    bash \
    nodejs \
    npm \
    wget \
    ca-certificates \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js v16.x and npm
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g webtorrent-cli

# Create a directory for SSL certificates
RUN mkdir -p /etc/nginx/ssl

# Generate a self-signed SSL certificate (valid for 365 days)
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/self-signed.key \
    -out /etc/nginx/ssl/self-signed.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=localhost"

# Generate a Diffie-Hellman group for added security
RUN openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048

# Download Mediamtx with SSL certificate validation disabled
RUN mkdir -p /opt/mediamtx && \
    cd /opt/mediamtx && \
    wget --no-check-certificate https://github.com/bluenviron/mediamtx/releases/download/v1.9.1/mediamtx_v1.9.1_linux_amd64.tar.gz && \
    tar -xvf mediamtx_v1.9.1_linux_amd64.tar.gz && \
    chmod +x mediamtx

# Create directories for HLS
RUN mkdir -p /app/static/hls

# Copy the custom Nginx configuration file to the container
COPY nginx.conf /etc/nginx/nginx.conf

# Expose ports for HTTP (80), HTTPS (443), and RTMP (1935)
EXPOSE 80 443 1935

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
