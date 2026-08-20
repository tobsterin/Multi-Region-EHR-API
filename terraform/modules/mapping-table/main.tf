resource "aws_dynamodb_table" "mapping_table" {
  name         = var.mapping_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "patient_uuid"

  attribute {
    name = "patient_uuid"
    type = "S"
  }
}