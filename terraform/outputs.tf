output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.app.id
}

output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.app.public_ip
}

output "instance_public_dns" {
  description = "Public DNS name of the EC2 instance"
  value       = aws_instance.app.public_dns
}

output "frontend_url" {
  description = "Frontend application URL"
  value       = "http://${aws_instance.app.public_ip}:3000"
}

output "backend_url" {
  description = "Backend API URL"
  value       = "http://${aws_instance.app.public_ip}:8000"
}

output "redis_cloud_info" {
  description = "Redis Cloud connection info"
  value       = "Using Redis Cloud: ${var.redis_url}"
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ~/.ssh/${var.key_pair_name}.pem ubuntu@${aws_instance.app.public_ip}"
}

output "view_logs_command" {
  description = "Command to view application logs"
  value       = "ssh -i ~/.ssh/${var.key_pair_name}.pem ubuntu@${aws_instance.app.public_ip} 'docker-compose -f /opt/banking-agent/docker-compose.yml logs -f'"
}

