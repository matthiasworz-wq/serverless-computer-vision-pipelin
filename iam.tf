data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_exec" {
  name               = "cv-lambda-exec-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

data "aws_iam_policy_document" "lambda_permissions" {
  statement {
    sid = "CloudWatchLogs"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = [
      "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"
    ]
  }

  statement {
    sid = "RekognitionRead"

    actions = [
      "rekognition:DetectLabels",
      "rekognition:DetectText"
    ]

    resources = ["*"]
  }

  statement {
    sid = "DynamoDBWrite"

    actions = ["dynamodb:PutItem"]

    resources = [aws_dynamodb_table.image_metadata.arn]
  }

  statement {
    sid = "S3ReadInputObjects"

    actions = ["s3:GetObject"]

    resources = ["${aws_s3_bucket.input.arn}/*"]
  }
}

resource "aws_iam_role_policy" "lambda_inline" {
  name   = "cv-lambda-inline-policy"
  role   = aws_iam_role.lambda_exec.id
  policy = data.aws_iam_policy_document.lambda_permissions.json
}
