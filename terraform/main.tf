terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Get default VPC if not specified
data "aws_vpc" "default" {
  count   = var.vpc_id == "" ? 1 : 0
  default = true
}

data "aws_vpc" "selected" {
  count = var.vpc_id != "" ? 1 : 0
  id    = var.vpc_id
}

locals {
  vpc_id = var.vpc_id != "" ? var.vpc_id : data.aws_vpc.default[0].id
}

# Get subnets in the VPC
data "aws_subnets" "available" {
  filter {
    name   = "vpc-id"
    values = [local.vpc_id]
  }
}

data "aws_subnet" "selected" {
  count = var.subnet_id != "" ? 1 : 0
  id    = var.subnet_id
}

data "aws_subnet" "default" {
  count = var.subnet_id == "" ? 1 : 0
  id    = data.aws_subnets.available.ids[0]
}

locals {
  subnet_id = var.subnet_id != "" ? var.subnet_id : data.aws_subnets.available.ids[0]
}

# Security Group for the application
resource "aws_security_group" "app_sg" {
  name        = "${var.project_name}-sg"
  description = "Security group for Banking Agent application"
  vpc_id      = local.vpc_id

  # SSH access
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.ssh_cidr_blocks
  }

  # Frontend (Next.js)
  ingress {
    description = "Frontend HTTP"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  # Backend API
  ingress {
    description = "Backend API"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  # All outbound traffic
  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.project_name}-sg"
  })
}

# EC2 Instance
resource "aws_instance" "app" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.app_sg.id]
  subnet_id              = local.subnet_id

  # Enable public IP if in public subnet
  associate_public_ip_address = true

  user_data = templatefile("${path.module}/user_data.sh", {
    github_repo_url          = var.github_repo_url
    github_branch            = var.github_branch
    openai_api_key           = var.openai_api_key
    redis_url                = var.redis_url
    history_index            = var.history_index
    history_namespace        = var.history_namespace
    history_topk_recent      = var.history_topk_recent
    history_topk_relevant    = var.history_topk_relevant
    history_distance_threshold = var.history_distance_threshold
  })

  root_block_device {
    volume_type = "gp3"
    volume_size = 30
    encrypted   = true
  }

  tags = merge(var.tags, {
    Name = "${var.project_name}-instance"
  })
}

# Get latest Ubuntu 22.04 LTS AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

