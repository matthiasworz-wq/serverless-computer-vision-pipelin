resource "aws_dynamodb_table" "metadata_table" {
  name         = "image-metadata-table"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "image_id"

  attribute {
    name = "image_id"
    type = "S"
  }
}