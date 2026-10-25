resource "aws_dynamodb_table" "metadata_table" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "image_id"

  point_in_time_recovery {
    enabled = false
  }

  server_side_encryption {
    enabled = true
  }

  attribute {
    name = "image_id"
    type = "S"
  }

  tags = {
    Project   = "serverless-computer-vision-pipeline"
    ManagedBy = "Terraform"
  }
}