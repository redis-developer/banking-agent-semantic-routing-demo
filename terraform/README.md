# Cloud Deployment Guide

This guide will help you deploy the Banking Agent Semantic Routing Demo to AWS EC2 using Terraform.

## Prerequisites

Before you begin, ensure you have:

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured (`aws configure`)
3. **Terraform** installed (>= 1.0)
4. **SSH Key Pair** created in AWS EC2
5. **OpenAI API Key** (for the banking agent)
6. **Redis Cloud Account** (or use local Redis)

## Step-by-Step Deployment

### 1. Clone the Repository

```bash
git clone https://github.com/redis-developer/banking-agent-semantic-routing-demo.git
cd banking-agent-semantic-routing-demo/terraform
```

### 2. Configure AWS Credentials

```bash
# Configure AWS CLI (if not already done)
aws configure

# Verify your credentials
aws sts get-caller-identity
```

### 3. Create SSH Key Pair in AWS

If you don't have an SSH key pair in AWS:

```bash
# Generate a new key pair locally
ssh-keygen -t rsa -b 4096 -f ~/.ssh/banking-agent-key

# Import to AWS (replace with your key name and region)
aws ec2 import-key-pair \
  --key-name "banking-agent-key" \
  --public-key-material fileb://~/.ssh/banking-agent-key.pub \
  --region us-east-1
```

Or create one via AWS Console:
- Go to EC2 → Key Pairs → Create Key Pair
- Download the `.pem` file and save it securely

### 4. Set Up Terraform Variables

```bash
# Copy the example file
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars  # or use your preferred editor
```

**Required Variables:**

```hcl
# AWS Configuration
aws_region    = "us-east-1"  # Change to your preferred region
instance_type = "t3.medium"  # t3.small, t3.medium, t3.large, etc.

# SSH Key Pair (must exist in AWS)
key_pair_name = "your-key-pair-name"

# OpenAI Configuration (REQUIRED)
openai_api_key = "sk-your-actual-openai-api-key"

# Redis Cloud Configuration (REQUIRED)
redis_url = "redis://default:password@your-redis-host:port"
# Or for SSL: rediss://default:password@your-redis-host:port
```

**Optional Variables:**

```hcl
# VPC Configuration (leave empty to use default VPC)
# vpc_id    = "vpc-xxxxxxxxx"
# subnet_id = "subnet-xxxxxxxxx"

# Security Configuration (recommended for production)
# Restrict SSH access to your IP
# ssh_cidr_blocks = ["YOUR_IP/32"]

# Restrict application access
# allowed_cidr_blocks = ["YOUR_IP/32"]

# GitHub Configuration (if using a fork)
# github_repo_url = "https://github.com/your-username/banking-agent-semantic-routing-demo.git"
# github_branch = "main"
```

### 5. Initialize Terraform

```bash
terraform init
```

This will download the required AWS provider plugins.

### 6. Review the Deployment Plan

```bash
terraform plan
```

Review the resources that will be created:
- EC2 instance
- Security group
- Network configuration

### 7. Deploy the Infrastructure

```bash
terraform apply
```

Type `yes` when prompted. This will:
- Create an EC2 instance
- Configure security groups
- Set up the application with Docker
- Pull the latest code from GitHub
- Start all services

**Deployment typically takes 5-10 minutes.**

### 8. Get the Application URL

After deployment completes, get the public IP:

```bash
terraform output public_ip
```

Or check the outputs:

```bash
terraform output
```

Access the application:
- **Frontend**: `http://<PUBLIC_IP>:3000`
- **Backend API**: `http://<PUBLIC_IP>:8000`

### 9. SSH into the Instance (Optional)

```bash
# Get the instance IP
PUBLIC_IP=$(terraform output -raw public_ip)

# SSH into the instance (replace with your key path)
ssh -i ~/.ssh/your-key.pem ubuntu@$PUBLIC_IP

# Once inside, check the application status
cd /opt/banking-agent
docker-compose ps
```

## Post-Deployment

### Update Code

To pull the latest code changes:

```bash
# SSH into the instance
ssh -i ~/.ssh/your-key.pem ubuntu@$(terraform output -raw public_ip)

# Pull latest code and restart
cd /opt/banking-agent
git pull origin main
docker-compose restart frontend backend
```

### View Logs

```bash
# SSH into the instance
ssh -i ~/.ssh/your-key.pem ubuntu@$(terraform output -raw public_ip)

# View logs
cd /opt/banking-agent
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Rebuild Containers

```bash
# SSH into the instance
ssh -i ~/.ssh/your-key.pem ubuntu@$(terraform output -raw public_ip)

# Rebuild and restart
cd /opt/banking-agent
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Troubleshooting

### Instance Not Accessible

1. **Check Security Groups**: Ensure ports 3000 and 8000 are open
2. **Check Instance Status**: `aws ec2 describe-instances --instance-ids <instance-id>`
3. **Check Application Logs**: SSH in and run `docker-compose logs`

### Application Not Starting

1. **Check Docker**: `docker ps` to see if containers are running
2. **Check Environment Variables**: Verify `.env` file in `/opt/banking-agent`
3. **Check Disk Space**: `df -h` (may need to clean up Docker: `docker system prune -a`)

### SSH Connection Issues

1. **Verify Key Permissions**: `chmod 400 ~/.ssh/your-key.pem`
2. **Check Security Group**: Ensure port 22 is open to your IP
3. **Use EC2 Instance Connect**: `aws ec2-instance-connect send-ssh-public-key`

## Cleanup

To destroy all resources and stop incurring costs:

```bash
terraform destroy
```

Type `yes` when prompted. This will:
- Terminate the EC2 instance
- Delete the security group
- Remove all associated resources

**⚠️ Warning**: This will permanently delete all data on the instance!

## Cost Estimation

Approximate monthly costs (varies by region and usage):

- **t3.small**: ~$15/month
- **t3.medium**: ~$30/month (recommended)
- **t3.large**: ~$60/month

Plus data transfer costs if applicable.

## Security Best Practices

1. **Restrict SSH Access**: Set `ssh_cidr_blocks` to your IP only
2. **Restrict Application Access**: Set `allowed_cidr_blocks` appropriately
3. **Use HTTPS**: Consider adding a load balancer with SSL certificate
4. **Rotate Keys**: Regularly rotate SSH keys and API keys
5. **Monitor Costs**: Set up AWS billing alerts

## Customization

### Change Instance Type

Edit `terraform.tfvars`:

```hcl
instance_type = "t3.large"  # For better performance
```

### Use Custom VPC

```hcl
vpc_id    = "vpc-xxxxxxxxx"
subnet_id = "subnet-xxxxxxxxx"
```

### Add Custom Tags

```hcl
tags = {
  Project     = "BankingAgent"
  Environment = "Production"
  Team        = "YourTeam"
  CostCenter  = "Engineering"
}
```

## Support

For issues or questions:
- Check the main [README.md](../README.md)
- Review Terraform logs: `terraform apply` output
- Check application logs: `docker-compose logs`
