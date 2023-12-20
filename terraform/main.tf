variable "aws_access_key" {
  description = "AWS Access Key"
  type        = string
}

variable "aws_secret_access_key" {
  description = "AWS Secret Key"
  type        = string
}

variable "mongodbatlas_public_key" {
  description = "MongoDB Atlas Public Key"
  type        = string
}

variable "mongodbatlas_private_key" {
  description = "MongoDB Atlas Private Key"
  type        = string
}

provider "aws" {
  region = "us-east-1"
  access_key = var.aws_access_key
  secret_key = var.aws_secret_access_key
}

resource "aws_s3_bucket" "ai_persona_app" {
  bucket = "ai-persona-app"
}

resource "aws_s3_bucket_policy" "my_bucket_policy" {
  bucket = aws_s3_bucket.ai_persona_app.id

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
          "${aws_s3_bucket.ai_persona_app.arn}",
          "${aws_s3_bucket.ai_persona_app.arn}/*"
        ]
      }
    ]
  })
}
