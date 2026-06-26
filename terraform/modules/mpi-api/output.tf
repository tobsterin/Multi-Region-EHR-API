output "mpi_api_url" {
  description = "The URL of the MPI API."
  value       = aws_apigatewayv2_stage.mpi_api_stage.invoke_url
}