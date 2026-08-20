variable "layer_name" {
  description = "The name of the Lambda layer."
  type        = string
  default     = "ehr-helpers"
}

variable "region_suffix" {
  description = "The suffix for the region."
  type        = string
}
