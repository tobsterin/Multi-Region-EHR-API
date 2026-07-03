output "table_name" {
    description = "The name of the DynamoDB table."
    value       = aws_dynamodb_table.patients.name
}
output "table_arn" {
    description = "The ARN of the DynamoDB table."
    value       = aws_dynamodb_table.patients.arn
}

output "stream_arn" {
  description = "The ARN of the DynamoDB stream"
  value = aws_dynamodb_table.patients.stream_arn
}