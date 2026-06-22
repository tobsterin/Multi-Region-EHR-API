resource "aws_cloudwatch_log_group" "patient_read_lambda_log_group" {
  name = "/aws/lambda/patient-read-lambda-${var.region_suffix}"
  retention_in_days = 14
}