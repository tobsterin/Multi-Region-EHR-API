output "patient_api_url" {
  description = "The URL of the patient API."
  value       = aws_apigatewayv2_stage.patient_api_stage.invoke_url
}