# read lambda logs:
resource "aws_cloudwatch_log_group" "encounters_read_lambda_log_group" {
  name              = "/aws/lambda/encounters-read-lambda-${var.region_suffix}"
  retention_in_days = 14
}

# write lambda logs:
resource "aws_cloudwatch_log_group" "encounters_write_lambda_log_group" {
  name              = "/aws/lambda/encounters-write-lambda-${var.region_suffix}"
  retention_in_days = 14
}

# update lambda logs:
resource "aws_cloudwatch_log_group" "encounters_update_lambda_log_group" {
  name              = "/aws/lambda/encounters-update-lambda-${var.region_suffix}"
  retention_in_days = 14
}
