# TODO: actually provision MongoDB
variable "mongodbatlas_public_key" {
  description = "MongoDB Atlas Public Key"
  type        = string
}

variable "mongodbatlas_private_key" {
  description = "MongoDB Atlas Private Key"
  type        = string
}

variable "aws_region" {
  description = "AWS Region"
  type        = string
}

variable "aws_access_key" {
  description = "AWS Access Key"
  type        = string
}

variable "aws_secret_access_key" {
  description = "AWS Secret Key"
  type        = string
}

provider "aws" {
  region = var.aws_region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_access_key
}

resource "aws_s3_bucket" "ai_persona_app_bucket" {
  bucket = "ai-persona-app"
}

resource "aws_s3_bucket_policy" "ai_persona_app_bucket_policy" {
  bucket = aws_s3_bucket.ai_persona_app_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = ["arn:aws:iam::912531404540:user/ai-persona-app", ]
        }
        Action = "s3:*"
        Resource = [
          "${aws_s3_bucket.ai_persona_app_bucket.arn}",
          "${aws_s3_bucket.ai_persona_app_bucket.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_ecr_repository" "ai_persona_app_ecr_repo" {
  name                 = "ai-persona-app"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

output "ai_persona_app_ecr_repo_url" {
  value = aws_ecr_repository.ai_persona_app_ecr_repo.repository_url
}

# TODO: split the below into a different terraform file, must have ECR repo and have pushed image to it before trying to set up ECS
resource "aws_ecs_cluster" "ai_persona_app_cluster" {
  name = "ai-persona-app"
}

resource "aws_ecs_task_definition" "ai_persona_app_task" {
  family                   = "ai-persona-app-task-family"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"

  container_definitions = jsonencode([{
    name  = "ai-persona-app-container",
    image = "ai_persona_app_ecr_repo_url:latest",
    portMappings = [{
      containerPort = 3000,
      hostPort      = 80
    }]
  }])
}



# TODO: invalid policy, is it needed?
# resource "aws_ecr_repository_policy" "ai_persona_app_ecr_policy" {
#   repository = aws_ecr_repository.ai_persona_app_ecr_repo.name

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow"
#         Principal = {
#           AWS = ["arn:aws:iam::912531404540:user/ai-persona-app"]
#         }
#         Action = [
#           "ecr:GetDownloadUrlForLayer",
#           "ecr:BatchGetImage",
#           "ecr:BatchCheckLayerAvailability",
#           "ecr:PutImage",
#           "ecr:InitiateLayerUpload",
#           "ecr:UploadLayerPart",
#           "ecr:CompleteLayerUpload"
#         ]
#         Resource = aws_ecr_repository.ai_persona_app_ecr_repo.arn
#       }
#     ]
#   })
# }
