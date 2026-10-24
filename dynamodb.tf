resource "aws_dynamodb_table" "image_metadata" {
  name         = "cv-image-metadata"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "image_id"

  attribute {
    name = "image_id"
    type = "S"
  }
}
