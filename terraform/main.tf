# cognito user pool and client for authentication:
module "cognito" {
  source    = "./modules/cognito"
  providers = { aws = aws.uk }
}

# Regional mapping tables: patient UUID -> that region's own patient ID.
# One per region, deliberately not global: the local patient ID never leaves its region.
module "mapping_table_de" {
  source             = "./modules/mapping-table"
  providers          = { aws = aws.de }
  mapping_table_name = "mapping_table_de"
}
module "mapping_table_fr" {
  source             = "./modules/mapping-table"
  providers          = { aws = aws.fr }
  mapping_table_name = "mapping_table_fr"
}
module "mapping_table_uk" {
  source             = "./modules/mapping-table"
  providers          = { aws = aws.uk }
  mapping_table_name = "mapping_table_uk"
}

# Global MPI (master patient index) and regional APIs:
module "mpi_table" {
  source    = "./modules/mpi-table"
  providers = { aws = aws.uk } # primary region; replicas handle de/fr
}

module "mpi_api_de" {
  source               = "./modules/mpi-api"
  region_suffix        = "de"
  table_arn            = module.mpi_table.table_arn
  lambda_layer_arn     = module.lambda_layer_de.layer_arn
  salt_param_name      = "/mpi/salt"
  cognito_client_id    = module.cognito.cognito_user_pool_client_id
  cognito_user_pool_id = module.cognito.cognito_user_pool_id
  providers            = { aws = aws.de }
}
module "mpi_registrar_de" {
  source             = "./modules/mpi-registrar"
  dynamodbstream_arn = module.regional_vault_de.stream_arn
  mapping_table_name = module.mapping_table_de.mapping_table_name
  mapping_table_arn  = module.mapping_table_de.mapping_table_arn
  lambda_layer_arn   = module.lambda_layer_de.layer_arn
  region_suffix      = "de"
  salt_param_name    = "/mpi/salt"
  providers          = { aws = aws.de }
}

module "mpi_api_fr" {
  source               = "./modules/mpi-api"
  region_suffix        = "fr"
  table_arn            = module.mpi_table.table_arn
  salt_param_name      = "/mpi/salt"
  cognito_client_id    = module.cognito.cognito_user_pool_client_id
  cognito_user_pool_id = module.cognito.cognito_user_pool_id
  lambda_layer_arn     = module.lambda_layer_fr.layer_arn
  providers            = { aws = aws.fr }
}
module "mpi_registrar_fr" {
  source             = "./modules/mpi-registrar"
  dynamodbstream_arn = module.regional_vault_fr.stream_arn
  mapping_table_name = module.mapping_table_fr.mapping_table_name
  mapping_table_arn  = module.mapping_table_fr.mapping_table_arn
  lambda_layer_arn   = module.lambda_layer_fr.layer_arn
  region_suffix      = "fr"
  salt_param_name    = "/mpi/salt"
  providers          = { aws = aws.fr }
}

module "mpi_api_uk" {
  source               = "./modules/mpi-api"
  region_suffix        = "uk"
  table_arn            = module.mpi_table.table_arn
  salt_param_name      = "/mpi/salt"
  cognito_client_id    = module.cognito.cognito_user_pool_client_id
  cognito_user_pool_id = module.cognito.cognito_user_pool_id
  lambda_layer_arn     = module.lambda_layer_uk.layer_arn
  providers            = { aws = aws.uk }
}
module "mpi_registrar_uk" {
  source             = "./modules/mpi-registrar"
  dynamodbstream_arn = module.regional_vault_uk.stream_arn
  mapping_table_name = module.mapping_table_uk.mapping_table_name
  mapping_table_arn  = module.mapping_table_uk.mapping_table_arn
  lambda_layer_arn   = module.lambda_layer_uk.layer_arn
  region_suffix      = "uk"
  salt_param_name    = "/mpi/salt"
  providers          = { aws = aws.uk }
}



# Regional providers:
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


# Regional patient vaults and APIs:
module "regional_vault_de" {
  source     = "./modules/regional-vault"
  table_name = "patients-de"
  providers  = { aws = aws.de }
}

module "patient_api_de" {
  source               = "./modules/patient-api"
  table_name           = module.regional_vault_de.table_name
  table_arn            = module.regional_vault_de.table_arn
  lambda_layer_arn     = module.lambda_layer_de.layer_arn
  cognito_client_id    = module.cognito.cognito_user_pool_client_id
  cognito_user_pool_id = module.cognito.cognito_user_pool_id
  region_suffix        = "de"
  providers            = { aws = aws.de }
}

module "regional_vault_fr" {
  source     = "./modules/regional-vault"
  table_name = "patients-fr"
  providers  = { aws = aws.fr }
}
module "patient_api_fr" {
  source               = "./modules/patient-api"
  table_name           = module.regional_vault_fr.table_name
  table_arn            = module.regional_vault_fr.table_arn
  lambda_layer_arn     = module.lambda_layer_fr.layer_arn
  cognito_client_id    = module.cognito.cognito_user_pool_client_id
  cognito_user_pool_id = module.cognito.cognito_user_pool_id
  region_suffix        = "fr"
  providers            = { aws = aws.fr }
}

module "regional_vault_uk" {
  source     = "./modules/regional-vault"
  table_name = "patients-uk"
  providers  = { aws = aws.uk }
}
module "patient_api_uk" {
  source               = "./modules/patient-api"
  table_name           = module.regional_vault_uk.table_name
  table_arn            = module.regional_vault_uk.table_arn
  lambda_layer_arn     = module.lambda_layer_uk.layer_arn
  cognito_client_id    = module.cognito.cognito_user_pool_client_id
  cognito_user_pool_id = module.cognito.cognito_user_pool_id
  region_suffix        = "uk"
  providers            = { aws = aws.uk }
}


# Regional clinical vaults:
module "clinical_vault_de" {
  source     = "./modules/clinical-vault"
  table_name = "clinical-de"
  providers  = { aws = aws.de }
}

module "clinical_vault_fr" {
  source     = "./modules/clinical-vault"
  table_name = "clinical-fr"
  providers  = { aws = aws.fr }
}

module "clinical_vault_uk" {
  source     = "./modules/clinical-vault"
  table_name = "clinical-uk"
  providers  = { aws = aws.uk }
}


# Regional encounters APIs:
module "encounters_api_de" {
  source               = "./modules/encounters-api"
  table_name           = module.clinical_vault_de.table_name
  table_arn            = module.clinical_vault_de.table_arn
  mapping_table_name   = module.mapping_table_de.mapping_table_name
  mapping_table_arn    = module.mapping_table_de.mapping_table_arn
  cognito_client_id    = module.cognito.cognito_user_pool_client_id
  cognito_user_pool_id = module.cognito.cognito_user_pool_id
  region_suffix        = "de"
  lambda_layer_arn     = module.lambda_layer_de.layer_arn
  providers            = { aws = aws.de }
}

module "encounters_api_fr" {
  source               = "./modules/encounters-api"
  table_name           = module.clinical_vault_fr.table_name
  table_arn            = module.clinical_vault_fr.table_arn
  mapping_table_name   = module.mapping_table_fr.mapping_table_name
  mapping_table_arn    = module.mapping_table_fr.mapping_table_arn
  cognito_client_id    = module.cognito.cognito_user_pool_client_id
  cognito_user_pool_id = module.cognito.cognito_user_pool_id
  region_suffix        = "fr"
  lambda_layer_arn     = module.lambda_layer_fr.layer_arn
  providers            = { aws = aws.fr }
}

module "encounters_api_uk" {
  source               = "./modules/encounters-api"
  table_name           = module.clinical_vault_uk.table_name
  table_arn            = module.clinical_vault_uk.table_arn
  mapping_table_name   = module.mapping_table_uk.mapping_table_name
  mapping_table_arn    = module.mapping_table_uk.mapping_table_arn
  cognito_client_id    = module.cognito.cognito_user_pool_client_id
  cognito_user_pool_id = module.cognito.cognito_user_pool_id
  region_suffix        = "uk"
  lambda_layer_arn     = module.lambda_layer_uk.layer_arn
  providers            = { aws = aws.uk }
}


# Regional observations APIs:
module "observations_api_de" {
  source               = "./modules/observations-api"
  table_name           = module.clinical_vault_de.table_name
  table_arn            = module.clinical_vault_de.table_arn
  mapping_table_name   = module.mapping_table_de.mapping_table_name
  mapping_table_arn    = module.mapping_table_de.mapping_table_arn
  cognito_client_id    = module.cognito.cognito_user_pool_client_id
  cognito_user_pool_id = module.cognito.cognito_user_pool_id
  region_suffix        = "de"
  lambda_layer_arn     = module.lambda_layer_de.layer_arn
  providers            = { aws = aws.de }
}

module "observations_api_fr" {
  source               = "./modules/observations-api"
  table_name           = module.clinical_vault_fr.table_name
  table_arn            = module.clinical_vault_fr.table_arn
  mapping_table_name   = module.mapping_table_fr.mapping_table_name
  mapping_table_arn    = module.mapping_table_fr.mapping_table_arn
  cognito_client_id    = module.cognito.cognito_user_pool_client_id
  cognito_user_pool_id = module.cognito.cognito_user_pool_id
  region_suffix        = "fr"
  lambda_layer_arn     = module.lambda_layer_fr.layer_arn
  providers            = { aws = aws.fr }
}

module "observations_api_uk" {
  source               = "./modules/observations-api"
  table_name           = module.clinical_vault_uk.table_name
  table_arn            = module.clinical_vault_uk.table_arn
  mapping_table_name   = module.mapping_table_uk.mapping_table_name
  mapping_table_arn    = module.mapping_table_uk.mapping_table_arn
  cognito_client_id    = module.cognito.cognito_user_pool_client_id
  cognito_user_pool_id = module.cognito.cognito_user_pool_id
  region_suffix        = "uk"
  lambda_layer_arn     = module.lambda_layer_uk.layer_arn
  providers            = { aws = aws.uk }
}

# Regional Lambda Layer:
module "lambda_layer_de" {
  source        = "./modules/lambda-layer"
  region_suffix = "de"
  providers     = { aws = aws.de }
}
module "lambda_layer_fr" {
  source        = "./modules/lambda-layer"
  region_suffix = "fr"
  providers     = { aws = aws.fr }
}
module "lambda_layer_uk" {
  source        = "./modules/lambda-layer"
  region_suffix = "uk"
  providers     = { aws = aws.uk }
}