# Use Debian-based image
FROM debian:bullseye-slim

# Install required packages, including build dependencies for Nginx and RTMP module
RUN apt update && apt install -y \
    openssl \
    libssl-dev \
    curl \
    build-essential \
    ffmpeg \
    libpcre3 \
    libpcre3-dev \
    libssl-dev \
    gcc \
    git \
    bash \
    libpcre3-dev \
    zlib1g-dev \
    libxslt1-dev \
    libgd-dev \
    libgeoip-dev \
    procps \
    nodejs \
    npm \
    wget \
    ca-certificates \
    nginx \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js v16.x and npm
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g webtorrent-cli

# Clone and build Nginx with RTMP module from source
RUN git clone https://github.com/sergey-dryabzhinsky/nginx-rtmp-module.git /tmp/nginx-rtmp-module && \
    wget http://nginx.org/download/nginx-1.17.6.tar.gz && \
    tar -xf nginx-1.17.6.tar.gzcd nginx-1.17.6 && \
    tar -zxvf nginx-1.21.6.tar.gz && \
    cd nginx-1.21.6 && \
    ./configure --prefix=/usr/local/nginx --with-http_ssl_module --add-module=../nginx-rtmp-modulemake -j && \
    make && \
    make install



# Create a directory for SSL certificates
RUN mkdir -p /etc/nginx/ssl

# Generate a self-signed SSL certificate (valid for 365 days)
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/self-signed.key \
    -out /etc/nginx/ssl/self-signed.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=localhost"

# Generate a Diffie-Hellman group for added security
RUN openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048

# Create directories for HLS
RUN mkdir -p /var/www/hls

# Copy the custom Nginx configuration file to the container
COPY nginx.conf /etc/nginx/nginx.conf

# Expose ports for HTTP (80), HTTPS (443), and RTMP (1935)
EXPOSE 443 1935

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
