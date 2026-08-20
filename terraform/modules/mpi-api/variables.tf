variable "table_arn" {
  description = "The ARN of the DynamoDB table."
  type        = string
}

variable "region_suffix" {
  description = "The suffix for the region."
  type        = string
}

variable "salt_param_name" {
  description = "The name of the SSM parameter for the salt."
  type        = string
  default     = "/mpi/salt"
}

# Cognito Variables:
variable "cognito_user_pool_id" {
  description = "The ID of the Cognito User Pool."
  type        = string
}

variable "cognito_client_id" {
  description = "The ID of the Cognito User Pool Client."
  type        = string
}

# Lambda Layer Variable:
variable "lambda_layer_arn" {
  description = "The ARN of the Lambda Layer."
  type        = string
}