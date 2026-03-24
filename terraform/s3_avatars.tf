resource "aws_s3_bucket" "avatars" {
  bucket = "${var.app_name}-avatars"
}

resource "aws_s3_bucket_public_access_block" "avatars" {
  bucket = aws_s3_bucket.avatars.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_cors_configuration" "avatars" {
  bucket = aws_s3_bucket.avatars.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET"]
    allowed_origins = ["https://${var.domain_name}"]
    max_age_seconds = 3600
  }
}
