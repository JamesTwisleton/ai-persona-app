output "frontend_url" {
  description = "Public URL for the frontend"
  value       = "https://${var.domain_name}"
}

output "api_url" {
  description = "Public URL for the backend API"
  value       = "https://${var.api_subdomain}"
}

output "alb_dns_name" {
  description = "ALB DNS name (for debugging)"
  value       = aws_lb.main.dns_name
}

output "ecr_backend_url" {
  description = "ECR repository URL for the backend image"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_frontend_url" {
  description = "ECR repository URL for the frontend image"
  value       = aws_ecr_repository.frontend.repository_url
}

output "rds_endpoint" {
  description = "RDS endpoint (internal, not publicly accessible)"
  value       = aws_db_instance.main.address
  sensitive   = true
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}
