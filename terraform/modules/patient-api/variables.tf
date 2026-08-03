variable "table_arn" {
  description = "The ARN of the DynamoDB table."
  type        = string
}

variable "region_suffix" {
  description = "The suffix for the region."
  type        = string
}

variable "table_name" {
  description = "The name of the DynamoDB table."
  type        = string
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