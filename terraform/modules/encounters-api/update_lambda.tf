data "archive_file" "encounters_update_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/src/update_encounters.py"
  output_path = "${path.module}/dist/update_encounters.zip"
}

resource "aws_lambda_function" "encounters_update_lambda" {
  function_name    = "encounters-update-lambda-${var.region_suffix}"
  role             = aws_iam_role.encounters_update_lambda_role.arn
  handler          = "update_encounters.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.encounters_update_lambda_zip.output_path
  source_code_hash = data.archive_file.encounters_update_lambda_zip.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = var.table_name
    }
  }

  depends_on = [
    aws_iam_role_policy.encounters_update_lambda_policy,
    aws_cloudwatch_log_group.encounters_update_lambda_log_group
  ]

}