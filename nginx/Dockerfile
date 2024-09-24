# Use Debian-based slim image
FROM debian:bullseye-slim

# Install required packages, including Nginx, build dependencies for Nginx, and RTMP module
RUN apt update && apt install -y \
    openssl \
    libssl-dev \
    curl \
    build-essential \
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
    gcc \
    ca-certificates \
    autoconf \
    automake \
    libtool \
    build-essential \
    gcc \
    make \
    pkg-config \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js v16.x and npm
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g webtorrent-cli




# Download Nginx source and build it with the RTMP module
RUN git clone https://github.com/arut/nginx-rtmp-module.git /tmp/nginx-rtmp-module

# Generate configure script if missing
RUN cd /tmp/nginx-rtmp-module && \
    if [ ! -f configure ]; then autoreconf -ivf; fi

# Configure and build Nginx with RTMP
RUN cd /tmp/nginx-rtmp-module && \
    ./configure --prefix=/usr/local/nginx --with-http_ssl_module --add-module=/tmp/nginx-rtmp-module && \
    make -j$(nproc) && \
    make install


RUN ./configure --prefix=/usr/local/nginx --with-http_ssl_module --add-module=/tmp/nginx-rtmp-module && \
    make -j$(nproc) && \
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

# Download Mediamtx with SSL certificate validation disabled
RUN mkdir -p /opt/mediamtx && \
    cd /opt/mediamtx && \
    wget --no-check-certificate https://github.com/bluenviron/mediamtx/releases/download/v1.9.1/mediamtx_v1.9.1_linux_amd64.tar.gz && \
    tar -xvf mediamtx_v1.9.1_linux_amd64.tar.gz && \
    chmod +x mediamtx

# Create directories for HLS
RUN mkdir -p /var/www/hls

# Copy the custom Nginx configuration file to the container
COPY nginx.conf /etc/nginx/nginx.conf

# Expose ports for HTTP (80), HTTPS (443), and RTMP (1935)
EXPOSE 443 1935

# Start Nginx
#CMD ["/usr/local/nginx/sbin/nginx", "-g", "daemon off;"]
CMD ["/usr/local/nginx", "-g", "daemon off;"]