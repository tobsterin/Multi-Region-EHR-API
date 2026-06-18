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
module "regional_vault_uk" {
  source     = "./modules/regional_vault"
  table_name = "patients-uk"
}

module "regional_vault_de" {
  source     = "./modules/regional_vault"
  table_name = "patients-de"
}

module "regional_vault_fr" {
  source     = "./modules/regional_vault"
  table_name = "patients-fr"
}