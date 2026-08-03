data "archive_file" "observations_write_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/src/write_observations.py"
  output_path = "${path.module}/dist/write_observations.zip"
}

resource "aws_lambda_function" "observations_write_lambda" {
  function_name    = "observations-write-lambda-${var.region_suffix}"
  role             = aws_iam_role.observations_write_lambda_role.arn
  handler          = "write_observations.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.observations_write_lambda_zip.output_path
  source_code_hash = data.archive_file.observations_write_lambda_zip.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = var.table_name
    }
  }

  depends_on = [
    aws_iam_role_policy.observations_write_lambda_policy,
    aws_cloudwatch_log_group.observations_write_lambda_log_group
  ]

}