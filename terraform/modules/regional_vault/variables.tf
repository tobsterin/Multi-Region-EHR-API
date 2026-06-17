variable "table_name" {
  description = "The name of the DynamoDB table."
  type        = string
  default     = "patients-uk"
}
variable  "attribute_name" {
  description = "The name of the attribute for the DynamoDB table."
  type        = string
  default     = "patient_id"
}