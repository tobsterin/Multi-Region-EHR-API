# Read Lambda Log Group:
resource "aws_cloudwatch_log_group" "mpi_read_lambda_log_group" {
  name = "/aws/lambda/mpi-read-lambda-${var.region_suffix}"
  retention_in_days = 14
}

# Write Lambda Log Group:
resource "aws_cloudwatch_log_group" "mpi_write_lambda_log_group" {
  name = "/aws/lambda/mpi-write-lambda-${var.region_suffix}"
  retention_in_days = 14
}