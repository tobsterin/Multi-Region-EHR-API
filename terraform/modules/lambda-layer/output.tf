output "layer_arn" {
  description = "The versioned ARN of the Lambda layer."
  value       = aws_lambda_layer_version.helpers.arn
}
