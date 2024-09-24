# Use the official Debian-based Nginx image as the base image
FROM debian:bullseye-slim

# Install required packages
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
    ffmpeg \
    vim \
    wget \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install Mediamtx RTMP Server (replacing the previous RTMP setup)
RUN mkdir -p /opt/mediamtx && \
    cd /opt/mediamtx && \
    VERSION=v1.5.0 && \
    wget https://github.com/bluenviron/mediamtx/releases/download/$VERSION/mediamtx_$VERSION_linux_amd64.tar.gz && \
    tar -xvf mediamtx_$VERSION_linux_amd64.tar.gz && \
    chmod +x mediamtx

# Create the Mediamtx service file
RUN cat <<'EOF' >/etc/systemd/system/mediamtx.service
[Unit]
Description=Mediamtx RTMP Service
ConditionPathExists=/opt/mediamtx
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/mediamtx
ExecStart=/opt/mediamtx/mediamtx /opt/mediamtx/mediamtx.yml

Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the Mediamtx service
RUN systemctl daemon-reload && \
    systemctl enable mediamtx.service && \
    systemctl start mediamtx.service

# Expose ports for RTMP and HTTP
EXPOSE 1935 8889

# Start the RTMP server
CMD ["/opt/mediamtx/mediamtx", "/opt/mediamtx/mediamtx.yml"]
