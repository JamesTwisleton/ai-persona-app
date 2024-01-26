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

# TODO: couldn't get ECS to access ECR with policies - maybe making it public will work? Should it be public?
resource "aws_ecr_repository_policy" "public_access" {
  repository = aws_ecr_repository.ai_persona_app_ecr_repo.name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid       = "PublicRead",
        Effect    = "Allow",
        Principal = "*",
        Action    = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability"
        ]
      }
    ]
  })
}
