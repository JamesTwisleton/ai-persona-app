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

resource "aws_ecr_repository_policy" "ai_persona_app_ecr_repo_policy" {
  repository = aws_ecr_repository.ai_persona_app_ecr_repo.name
  policy     = jsonencode({
    Version = "2008-10-17",
    Statement = [
      {
        Sid    = "ECRAccess",
        Effect = "Allow",
        Principal = {
          AWS = aws_iam_role.ai_persona_app_ecs_execution_role.arn
        },
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:BatchGetImage",
          "ecr:CompleteLayerUpload",
          "ecr:GetDownloadUrlForLayer",
          "ecr:GetLifecyclePolicy",
          "ecr:InitiateLayerUpload",
          "ecr:PutImage",
          "ecr:UploadLayerPart"
        ]
      }
    ]
  })
}
