data "archive_file" "observations_update_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/src/update_observations.py"
  output_path = "${path.module}/dist/update_observations.zip"
}

resource "aws_lambda_function" "observations_update_lambda" {
  function_name    = "observations-update-lambda-${var.region_suffix}"
  role             = aws_iam_role.observations_update_lambda_role.arn
  handler          = "update_observations.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.observations_update_lambda_zip.output_path
  source_code_hash = data.archive_file.observations_update_lambda_zip.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = var.table_name
    }
  }

  depends_on = [
    aws_iam_role_policy.observations_update_lambda_policy,
    aws_cloudwatch_log_group.observations_update_lambda_log_group
  ]
  
}