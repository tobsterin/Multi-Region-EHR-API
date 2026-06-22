provider "aws" {
  alias  = "de"
  region = "eu-central-1"
  default_tags {
    tags = {
      Environment = var.environment
      Project     = "multi-region-ehr-api"
      ManagedBy   = "terraform"
      DataClass   = "synthetic-phi"
    }
  }
}

provider "aws" {
  alias  = "fr"
  region = "eu-west-3"
  default_tags {
    tags = {
      Environment = var.environment
      Project     = "multi-region-ehr-api"
      ManagedBy   = "terraform"
      DataClass   = "synthetic-phi"
    }
  }
}

provider "aws" {
  alias  = "uk"
  region = "eu-west-2"

  default_tags {
    tags = {
      Environment = var.environment
      Project     = "multi-region-ehr-api"
      ManagedBy   = "terraform"
      DataClass   = "synthetic-phi"
    }
  }
}

module "regional_vault_de" {
  source     = "./modules/regional-vault"
  table_name = "patients-de"
  providers  = { aws = aws.de }
}
module "patient_api_de" {
  source        = "./modules/patient-api"
  table_name    = module.regional_vault_de.table_name
  table_arn     = module.regional_vault_de.table_arn
  region_suffix = "de"
  providers     = { aws = aws.de }
}

module "regional_vault_fr" {
  source     = "./modules/regional-vault"
  table_name = "patients-fr"
  providers  = { aws = aws.fr }
}
module "patient_api_fr" {
  source        = "./modules/patient-api"
  table_name    = module.regional_vault_fr.table_name
  table_arn     = module.regional_vault_fr.table_arn
  region_suffix = "fr"
  providers     = { aws = aws.fr }
}

module "regional_vault_uk" {
  source     = "./modules/regional-vault"
  table_name = "patients-uk"
  providers  = { aws = aws.uk }
}
module "patient_api_uk" {
  source        = "./modules/patient-api"
  table_name    = module.regional_vault_uk.table_name
  table_arn     = module.regional_vault_uk.table_arn
  region_suffix = "uk"
  providers     = { aws = aws.uk }
}