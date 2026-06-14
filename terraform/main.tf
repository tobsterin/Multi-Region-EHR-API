provider "aws" {
    region = "eu-west-2"

    default_tags {
        tags = {
            Environment = "dev"
            Project     = "multi-region-ehr-api"
            ManagedBy  = "terraform"
            DataClass = "synthetic-phi"
        }
    }
}
resource "aws_dynamodb_table" "patients_uk" {
  name         = "patients-uk"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "patient_id"

  attribute {
    name = "patient_id"
    type = "S"
  }
}