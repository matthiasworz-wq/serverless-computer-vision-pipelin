variable "aws_region" {
  description = "AWS region for all resources."
  type        = string
  default     = "eu-north-1"
}

variable "aws_profile" {
  description = "Optional local AWS CLI profile. Leave null when using environment credentials."
  type        = string
  default     = null
}

variable "bucket_name" {
  description = "Globally unique private S3 bucket name for image uploads."
  type        = string
  default     = "vision-pipeline-input-matthias-worz"
}

variable "table_name" {
  description = "DynamoDB table for image metadata."
  type        = string
  default     = "image-metadata-table"
}

variable "lambda_function_name" {
  description = "Name of the image-processing Lambda function."
  type        = string
  default     = "image-vision-processor"
}

variable "resource_name_suffix" {
  description = "Optional suffix used to distinguish resources in a shared AWS account."
  type        = string
  default     = "matthias"
}
