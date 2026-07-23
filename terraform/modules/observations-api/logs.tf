# read lambda logs:
resource "aws_cloudwatch_log_group" "observations_read_lambda_log_group" {
  name = "/aws/lambda/observations-read-lambda-${var.region_suffix}"
  retention_in_days = 14
}

# write lambda logs:
resource "aws_cloudwatch_log_group" "observations_write_lambda_log_group" {
  name = "/aws/lambda/observations-write-lambda-${var.region_suffix}"
  retention_in_days = 14
}

# update lambda logs:
resource "aws_cloudwatch_log_group" "observations_update_lambda_log_group" {
  name = "/aws/lambda/observations-update-lambda-${var.region_suffix}"
  retention_in_days = 14
}
