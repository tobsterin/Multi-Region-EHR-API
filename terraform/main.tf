provider "aws" {
    region = var.region

    default_tags {
        tags = {
            Environment = var.environment
            Project     = "multi-region-ehr-api"
            ManagedBy  = "terraform"
            DataClass = "synthetic-phi"
        }
    }
}
module "regional-vault-uk" {
    source = "./modules/regional_vault"
    table_name = "patients-uk"
}