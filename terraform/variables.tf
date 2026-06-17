variable "region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "eu-west-2"
  
}
variable "environment" {
  description = "The environment to deploy resources in (e.g., dev, staging, prod)."
  type        = string
  default     = "dev"
}