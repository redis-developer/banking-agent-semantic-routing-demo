#!/bin/bash
set -e

# Update system
apt-get update -y
apt-get upgrade -y

# Install required packages
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    wget \
    unzip

# Install Docker
if ! command -v docker &> /dev/null; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    systemctl enable docker
    systemctl start docker
    usermod -aG docker ubuntu
fi

# Install Docker Compose (standalone, if not using plugin)
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
fi

# Create docker-compose alias if using plugin version
if ! command -v docker-compose &> /dev/null && docker compose version &> /dev/null; then
    cat > /usr/local/bin/docker-compose <<'EOF'
#!/bin/bash
docker compose "$@"
EOF
    chmod +x /usr/local/bin/docker-compose
fi

# Create application directory
APP_DIR="/opt/banking-agent"
mkdir -p $APP_DIR
cd $APP_DIR

# Clone repository
if [ ! -d "$APP_DIR/.git" ]; then
    git clone -b ${github_branch} ${github_repo_url} .
else
    cd $APP_DIR
    git fetch origin
    git checkout ${github_branch}
    git pull origin ${github_branch}
fi

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

# Create .env file
cat > $APP_DIR/.env <<EOF
OPENAI_API_KEY=${openai_api_key}
REDIS_URL=${redis_url}
HISTORY_INDEX=${history_index}
HISTORY_NAMESPACE=${history_namespace}
HISTORY_TOPK_RECENT=${history_topk_recent}
HISTORY_TOPK_RELEVANT=${history_topk_relevant}
HISTORY_DISTANCE_THRESHOLD=${history_distance_threshold}
CORS_ORIGINS=http://localhost:3000,http://$PUBLIC_IP:3000
NEXT_PUBLIC_API_BASE=http://$PUBLIC_IP:8000
EOF

# Export environment variables so docker-compose can use them
export OPENAI_API_KEY=${openai_api_key}
export REDIS_URL=${redis_url}
export HISTORY_INDEX=${history_index}
export HISTORY_NAMESPACE=${history_namespace}
export HISTORY_TOPK_RECENT=${history_topk_recent}
export HISTORY_TOPK_RELEVANT=${history_topk_relevant}
export HISTORY_DISTANCE_THRESHOLD=${history_distance_threshold}
export CORS_ORIGINS="http://localhost:3000,http://$PUBLIC_IP:3000"
export NEXT_PUBLIC_API_BASE="http://$PUBLIC_IP:8000"

# Update docker-compose.yml to use environment variables from .env
sed -i "s|NEXT_PUBLIC_API_BASE=.*|NEXT_PUBLIC_API_BASE=\${NEXT_PUBLIC_API_BASE:-http://$PUBLIC_IP:8000}|g" $APP_DIR/docker-compose.yml || true
sed -i "s|CORS_ORIGINS=.*|CORS_ORIGINS=\${CORS_ORIGINS:-http://localhost:3000,http://$PUBLIC_IP:3000}|g" $APP_DIR/docker-compose.yml || true

# Build and start containers
cd $APP_DIR
# Try docker-compose first, fallback to docker compose
if command -v docker-compose &> /dev/null; then
    docker-compose down || true
    docker-compose build --no-cache
    docker-compose up -d
elif docker compose version &> /dev/null; then
    docker compose down || true
    docker compose build --no-cache
    docker compose up -d
else
    echo "ERROR: Neither docker-compose nor docker compose found!"
    exit 1
fi

# Wait for services to be healthy
echo "Waiting for services to start..."
sleep 30

# Restart frontend to ensure it picks up NEXT_PUBLIC_API_BASE environment variable
# (Next.js needs this at startup, not just build time)
if command -v docker-compose &> /dev/null; then
    docker-compose restart frontend
    docker-compose ps
elif docker compose version &> /dev/null; then
    docker compose restart frontend
    docker compose ps
fi

# Create systemd service for auto-start on reboot
cat > /etc/systemd/system/banking-agent.service <<'SERVICE_EOF'
[Unit]
Description=Banking Agent Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/banking-agent
ExecStart=/bin/bash -c 'cd /opt/banking-agent && (command -v docker-compose >/dev/null && docker-compose up -d || docker compose up -d)'
ExecStop=/bin/bash -c 'cd /opt/banking-agent && (command -v docker-compose >/dev/null && docker-compose down || docker compose down)'
User=root

[Install]
WantedBy=multi-user.target
SERVICE_EOF

systemctl daemon-reload
systemctl enable banking-agent.service

# Log completion
echo "Deployment completed at $(date)" >> /var/log/banking-agent-deploy.log
echo "Public IP: $PUBLIC_IP" >> /var/log/banking-agent-deploy.log
echo "Frontend: http://$PUBLIC_IP:3000" >> /var/log/banking-agent-deploy.log
echo "Backend: http://$PUBLIC_IP:8000" >> /var/log/banking-agent-deploy.log

