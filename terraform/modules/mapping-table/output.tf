output "mapping_table_name" {
  description = "The name of the DynamoDB table."
  value       = aws_dynamodb_table.mapping_table.name
}

output "mapping_table_arn" {
  description = "The ARN of the DynamoDB table."
  value       = aws_dynamodb_table.mapping_table.arn
}