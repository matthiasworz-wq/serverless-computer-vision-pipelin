output "s3_bucket_name" {
  value = aws_s3_bucket.image_bucket.id
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.metadata_table.id
}

output "lambda_function_name" {
  value = aws_lambda_function.vision_processor.function_name
}

output "lambda_dlq_url" {
  value = aws_sqs_queue.lambda_dlq.url
}

output "aws_region" {
  value = var.aws_region
}