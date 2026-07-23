output "encounters_api_url" {
  description = "The URL of the encounters API."
  value       = aws_apigatewayv2_stage.encounters_api_stage.invoke_url
}