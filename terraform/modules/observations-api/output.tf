output "observations_api_url" {
  description = "The URL of the observations API."
  value       = aws_apigatewayv2_stage.observations_api_stage.invoke_url
}