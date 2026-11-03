resource "aws_lambda_function" "vision_processor" {
  filename                       = "${path.module}/lambda.zip"
  function_name                  = var.lambda_function_name
  role                           = aws_iam_role.lambda_role.arn
  handler                        = "handler.handler"
  runtime                        = "python3.12"
  timeout                        = 30
  memory_size                    = 128
  reserved_concurrent_executions = 1
  source_code_hash               = filebase64sha256("${path.module}/lambda.zip")

  environment {
    variables = {
      TABLE_NAME      = aws_dynamodb_table.metadata_table.name
      MAX_IMAGE_BYTES = "10485760"
    }
  }

  tags = {
    Project   = "serverless-computer-vision-pipeline"
    ManagedBy = "Terraform"
  }
}

resource "aws_cloudwatch_log_group" "vision_processor" {
  name              = "/aws/lambda/${aws_lambda_function.vision_processor.function_name}"
  retention_in_days = 7

  tags = {
    Project   = "serverless-computer-vision-pipeline"
    ManagedBy = "Terraform"
  }
}

resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.vision_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.image_bucket.arn
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.image_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.vision_processor.arn
    events              = ["s3:ObjectCreated:*"]

    filter_suffix = ".jpg"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.vision_processor.arn
    events              = ["s3:ObjectCreated:*"]

    filter_suffix = ".jpeg"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.vision_processor.arn
    events              = ["s3:ObjectCreated:*"]

    filter_suffix = ".png"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}

resource "aws_lambda_function_event_invoke_config" "vision_processor" {
  function_name          = aws_lambda_function.vision_processor.function_name
  maximum_retry_attempts = 1

  destination_config {
    on_failure {
      destination = aws_sqs_queue.lambda_dlq.arn
    }
  }
}

resource "aws_sqs_queue" "lambda_dlq" {
  name                      = "vision-pipeline-lambda-dlq-${var.resource_name_suffix}"
  message_retention_seconds = 86400
  sqs_managed_sse_enabled   = true

  tags = {
    Project   = "serverless-computer-vision-pipeline"
    ManagedBy = "Terraform"
  }
}