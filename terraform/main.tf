provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = "multi-region-ehr-api"
      ManagedBy   = "terraform"
      DataClass   = "synthetic-phi"
    }
  }
}
module "regional-vault-uk" {
  source     = "./modules/regional_vault"
  table_name = "patients-uk"
}

module "regional-vault-de" {
  source     = "./modules/regional_vault"
  table_name = "patients-de"
}

module "regional-vault-fr" {
  source     = "./modules/regional_vault"
  table_name = "patients-fr"
}