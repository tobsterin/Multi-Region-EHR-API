output "table_name_de" {
  description = "The name of the DynamoDB table in the DE region."
  value       = module.regional_vault_de.table_name
}
output "table_arn_de" {
  description = "The ARN of the DynamoDB table in the DE region."
  value       = module.regional_vault_de.table_arn
}

output "patient_api_url_de" {
  value = module.patient_api_de.patient_api_url
}

output "table_name_fr" {
  description = "The name of the DynamoDB table in the FR region."
  value       = module.regional_vault_fr.table_name
}
output "table_arn_fr" {
  description = "The ARN of the DynamoDB table in the FR region."
  value       = module.regional_vault_fr.table_arn
}

output "patient_api_url_fr" {
  value = module.patient_api_fr.patient_api_url
}

output "table_name_uk" {
  description = "The name of the DynamoDB table in the UK region."
  value       = module.regional_vault_uk.table_name
}

output "table_arn_uk" {
  description = "The ARN of the DynamoDB table in the UK region."
  value       = module.regional_vault_uk.table_arn
}

output "patient_api_url_uk" {
  value = module.patient_api_uk.patient_api_url
}