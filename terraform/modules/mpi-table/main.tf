resource "aws_dynamodb_table" "mpi_table" {
  name             = "mpi_global_table"
  billing_mode     = "PAY_PER_REQUEST"
  hash_key         = "national_id_hash"
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  # One item per hash, so a hash can only ever hold one identity.
  attribute {
    name = "national_id_hash"
    type = "S"
  }
  attribute {
    name = "patient_uuid"
    type = "S"
  }
  attribute {
    name = "region"
    type = "S"
  }

  # Every region a UUID is registered in, for the federated read fan-out.
  # Index keys need not be unique, so this doesn't weaken the rule above.
  global_secondary_index {
    name            = "patient_uuid_index"
    hash_key        = "patient_uuid"
    range_key       = "region"
    projection_type = "KEYS_ONLY"
  }

  replica {
    region_name = "eu-central-1"
  }
  replica {
    region_name = "eu-west-3"
  }
}