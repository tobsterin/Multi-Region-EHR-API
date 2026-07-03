resource "aws_cloudwatch_log_group" "mpi_registrar_lambda_log_group" {
    name = "/aws/lambda/mpi-registrar-lambda-${var.region_suffix}"
    retention_in_days = 14
}