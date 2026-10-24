output "s3_bucket_name" {
  description = "Name of the S3 input bucket"
  value       = aws_s3_bucket.input.bucket
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB metadata table"
  value       = aws_dynamodb_table.image_metadata.name
}
