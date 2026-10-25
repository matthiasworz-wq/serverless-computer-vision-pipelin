resource "aws_s3_bucket" "image_bucket" {
  bucket        = var.bucket_name
  force_destroy = true

  tags = {
    Project   = "serverless-computer-vision-pipeline"
    ManagedBy = "Terraform"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "image_bucket" {
  bucket = aws_s3_bucket.image_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "image_bucket" {
  bucket = aws_s3_bucket.image_bucket.id

  rule {
    id     = "delete-test-images"
    status = "Enabled"

    filter {}

    expiration {
      days = 7
    }
  }
}

resource "aws_s3_bucket_public_access_block" "block" {
  bucket                  = aws_s3_bucket.image_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}