variable "dynamodbstream_arn" {
  description = "The ARN of the DynamoDB stream"
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

variable "mapping_table_name" {
  description = "The name of the DynamoDB mapping table."
  type        = string
}

variable "mapping_table_arn" {
  description = "The ARN of the MPI table."
  type        = string
}


# Lambda Layer Variable:
variable "lambda_layer_arn" {
  description = "The ARN of the Lambda Layer."
  type        = string
}