# read lambda logs:
resource "aws_cloudwatch_log_group" "patient_read_lambda_log_group" {
  name              = "/aws/lambda/patient-read-lambda-${var.region_suffix}"
  retention_in_days = 14
}

# write lambda logs:
resource "aws_cloudwatch_log_group" "patient_write_lambda_log_group" {
  name              = "/aws/lambda/patient-write-lambda-${var.region_suffix}"
  retention_in_days = 14
}

# update lambda logs:
resource "aws_cloudwatch_log_group" "patient_update_lambda_log_group" {
  name              = "/aws/lambda/patient-update-lambda-${var.region_suffix}"
  retention_in_days = 14
}
