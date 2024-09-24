# Use the official Nginx image as the base image
FROM maquinas07/alpine-nginx-rtmp

# Install the required packages, including build dependencies for Nginx and RTMP module
RUN apk add --no-cache \
    openssl \
    openssl-dev \
    pcre-dev \
    zlib-dev \
    gcc \
    libc-dev \
    make \
    libxslt-dev \
    gd-dev \
    geoip-dev \
    git \
    bash \
    curl \
    python3-dev \
    libffi-dev \
    libressl-dev \
    nodejs \
    npm \
    net-tools \
    procps

# Clone and build Nginx with RTMP module from source
RUN git clone https://github.com/arut/nginx-rtmp-module.git /tmp/nginx-rtmp-module && \
    wget http://nginx.org/download/nginx-1.21.6.tar.gz && \
    tar -zxvf nginx-1.21.6.tar.gz && \
    cd nginx-1.21.6 && \
    ./configure --with-http_ssl_module --add-module=/tmp/nginx-rtmp-module && \
    make && make install

# Create a directory for SSL certificates
RUN mkdir /etc/nginx/ssl

# Generate a self-signed SSL certificate (valid for 365 days)
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/self-signed.key \
    -out /etc/nginx/ssl/self-signed.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=localhost"

# Generate a Diffie-Hellman group for added security
RUN openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048

# Install WebTorrent (using npm)
RUN npm install -g webtorrent-cli

# Create directories for HLS
RUN mkdir /var/www && mkdir /var/www/hls

# Copy the custom Nginx configuration file to the container
COPY nginx.conf /etc/nginx/nginx.conf

# Expose ports for HTTP (80), HTTPS (443), and RTMP (1935)
EXPOSE 443 1935

# Start Nginx (default command is already provided by the base image)
CMD ["nginx", "-g", "daemon off;", "-c", "/etc/nginx/nginx.conf", "-e", "debug"]
