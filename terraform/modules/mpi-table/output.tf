output "table_arn" {
  description = "The ARN of the DynamoDB table."
  value       = aws_dynamodb_table.mpi_table.arn
}