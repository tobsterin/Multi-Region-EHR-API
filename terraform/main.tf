# Global MPI (master patient index) and regional APIs:
module "mpi_table" {
  source    = "./modules/mpi-table"
  providers = { aws = aws.uk } # primary region; replicas handle de/fr
}

module "mpi_api_de" {
  source        = "./modules/mpi-api"
  region_suffix = "de"
  table_arn     = module.mpi_table.table_arn
  providers     = { aws = aws.de }
}
module "mpi_registrar_de" {
  source             = "./modules/mpi-registrar"
  table_arn          = module.mpi_table.table_arn
  dynamodbstream_arn = module.regional_vault_de.stream_arn
  region_suffix      = "de"
  providers          = { aws = aws.de }
}

module "mpi_api_fr" {
  source        = "./modules/mpi-api"
  region_suffix = "fr"
  table_arn     = module.mpi_table.table_arn
  providers     = { aws = aws.fr }
}
module "mpi_registrar_fr" {
  source             = "./modules/mpi-registrar"
  table_arn          = module.mpi_table.table_arn
  dynamodbstream_arn = module.regional_vault_fr.stream_arn
  region_suffix      = "fr"
  providers          = { aws = aws.fr }
}

module "mpi_api_uk" {
  source        = "./modules/mpi-api"
  region_suffix = "uk"
  table_arn     = module.mpi_table.table_arn
  providers     = { aws = aws.uk }
}
module "mpi_registrar_uk" {
  source             = "./modules/mpi-registrar"
  table_arn          = module.mpi_table.table_arn
  dynamodbstream_arn = module.regional_vault_uk.stream_arn
  region_suffix      = "uk"
  providers          = { aws = aws.uk }
}



# Regional patient vaults and APIs:
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