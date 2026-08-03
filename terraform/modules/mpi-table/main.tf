resource "aws_dynamodb_table" "mpi_table" {
  name             = "mpi_global_table"
  billing_mode     = "PAY_PER_REQUEST"
  hash_key         = "patient_uuid"
  range_key        = "region"
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  attribute {
    name = "patient_uuid"
    type = "S"
  }
  attribute {
    name = "region"
    type = "S"
  }
  attribute {
    name = "national_id_hash"
    type = "S"
  }

  global_secondary_index {
    name            = "national_id_hash_index"
    hash_key        = "national_id_hash"
    projection_type = "ALL"
  }
  replica {
    region_name = "eu-central-1"
  }
  replica {
    region_name = "eu-west-3"
  }
}