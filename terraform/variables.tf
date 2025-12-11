variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"  # Minimum recommended for Docker workloads
}

variable "key_pair_name" {
  description = "Name of the AWS key pair for SSH access"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID (leave empty to use default VPC)"
  type        = string
  default     = ""
}

variable "subnet_id" {
  description = "Subnet ID (leave empty to use default subnet)"
  type        = string
  default     = ""
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}

variable "redis_url" {
  description = "Redis Cloud URL (e.g., redis://default:password@host:port or rediss:// for SSL)"
  type        = string
  # No default - must be provided for Redis Cloud
}

variable "history_index" {
  description = "Redis history index name"
  type        = string
  default     = "bank:msg:index"
}

variable "history_namespace" {
  description = "Redis history namespace"
  type        = string
  default     = "bank:chat"
}

variable "history_topk_recent" {
  description = "Number of recent messages to retrieve"
  type        = number
  default     = 8
}

variable "history_topk_relevant" {
  description = "Number of relevant messages to retrieve"
  type        = number
  default     = 6
}

variable "history_distance_threshold" {
  description = "Distance threshold for relevant messages"
  type        = number
  default     = 0.35
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the application (0.0.0.0/0 for public)"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "ssh_cidr_blocks" {
  description = "CIDR blocks allowed for SSH access"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # Restrict this in production!
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "banking-agent"
}

variable "github_repo_url" {
  description = "GitHub repository URL"
  type        = string
  default     = "https://github.com/redis-developer/banking-agent-semantic-routing-demo.git"
}

variable "github_branch" {
  description = "GitHub branch to deploy"
  type        = string
  default     = "main"
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    Project     = "BankingAgent"
    Environment = "Production"
    ManagedBy   = "Terraform"
  }
}

