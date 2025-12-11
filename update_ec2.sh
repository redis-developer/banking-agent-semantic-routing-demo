#!/bin/bash
# Script to update the EC2 instance with latest code changes
# Usage: ./update_ec2.sh <instance-ip> <ssh-key-path>

INSTANCE_IP=${1:-"3.107.237.10"}
SSH_KEY=${2:-"~/.ssh/semantic_routing_demo.pem"}

echo "Updating EC2 instance at $INSTANCE_IP..."

# Update the frontend code
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ubuntu@$INSTANCE_IP << 'EOF'
cd /opt/banking-agent

# Pull latest code
git pull origin main || echo "Git pull failed, continuing..."

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

# Update .env file
cat > .env <<ENVEOF
$(cat .env | grep -v NEXT_PUBLIC_API_BASE | grep -v CORS_ORIGINS)
CORS_ORIGINS=http://localhost:3000,http://$PUBLIC_IP:3000
NEXT_PUBLIC_API_BASE=http://$PUBLIC_IP:8000
ENVEOF

# Update docker-compose.yml environment variables
sed -i "s|NEXT_PUBLIC_API_BASE=.*|NEXT_PUBLIC_API_BASE=\${NEXT_PUBLIC_API_BASE:-http://$PUBLIC_IP:8000}|g" docker-compose.yml
sed -i "s|CORS_ORIGINS=.*|CORS_ORIGINS=\${CORS_ORIGINS:-http://localhost:3000,http://$PUBLIC_IP:3000}|g" docker-compose.yml

# Restart containers to pick up changes
if command -v docker-compose &> /dev/null; then
    docker-compose restart frontend backend
elif docker compose version &> /dev/null; then
    docker compose restart frontend backend
fi

echo "Update complete!"
EOF

echo "Done! Frontend should now connect to the backend."

