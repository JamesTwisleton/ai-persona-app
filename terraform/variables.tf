variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "app_name" {
  description = "Application name, used for resource naming"
  type        = string
  default     = "persona-composer"
}

variable "domain_name" {
  description = "Root domain name"
  type        = string
  default     = "personacomposer.app"
}

variable "api_subdomain" {
  description = "Subdomain for the backend API"
  type        = string
  default     = "api.personacomposer.app"
}

# ============================================================
# Secrets (stored in Secrets Manager, passed via tfvars)
# ============================================================

variable "anthropic_api_key" {
  description = "Anthropic API key for Claude"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key for DALL-E and moderation"
  type        = string
  sensitive   = true
}

variable "jwt_secret" {
  description = "JWT signing secret"
  type        = string
  sensitive   = true
}

variable "google_client_id" {
  description = "Google OAuth client ID"
  type        = string
  sensitive   = true
}

variable "google_client_secret" {
  description = "Google OAuth client secret"
  type        = string
  sensitive   = true
}

# ============================================================
# Database
# ============================================================

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "persona_composer"
}

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "persona_composer_user"
}

variable "db_instance_class" {
  description = "RDS instance type"
  type        = string
  default     = "db.t3.micro"
}

# ============================================================
# ECS
# ============================================================

variable "backend_cpu" {
  description = "CPU units for backend ECS task (1024 = 1 vCPU)"
  type        = number
  default     = 512
}

variable "backend_memory" {
  description = "Memory (MB) for backend ECS task"
  type        = number
  default     = 1024
}

variable "frontend_cpu" {
  description = "CPU units for frontend ECS task"
  type        = number
  default     = 256
}

variable "frontend_memory" {
  description = "Memory (MB) for frontend ECS task"
  type        = number
  default     = 512
}
