variable "environment" {
  description = "The environment to deploy resources in (e.g., dev, staging, prod)."
  type        = string
  default     = "dev"
}

# Lambda Layer Variable:
variable "lambda_layer_arn" {
  description = "The ARN of the Lambda Layer."
  type        = string
}