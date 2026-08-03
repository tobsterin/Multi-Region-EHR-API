resource "aws_dynamodb_table" "patients" {
  name             = var.table_name
  billing_mode     = "PAY_PER_REQUEST"
  hash_key         = var.attribute_name
  stream_enabled   = true
  stream_view_type = "NEW_IMAGE"

  attribute {
    name = var.attribute_name
    type = "S"
  }
}