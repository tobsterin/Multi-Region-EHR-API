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