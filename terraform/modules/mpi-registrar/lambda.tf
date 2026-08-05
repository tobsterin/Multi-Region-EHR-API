data "archive_file" "mpi_registrar_archive" {
  type        = "zip"
  source_file = "${path.module}/src/mpi_registrar.py"
  output_path = "${path.module}/dist/mpi_registrar.zip"
}

resource "aws_lambda_function" "mpi_registrar_lambda" {
  function_name    = "mpi-registrar-lambda-${var.region_suffix}"
  role             = aws_iam_role.mpi_registrar_lambda_role.arn
  handler          = "mpi_registrar.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.mpi_registrar_archive.output_path
  source_code_hash = data.archive_file.mpi_registrar_archive.output_base64sha256

  environment {
    variables = {
      TABLE_NAME      = "mpi_global_table"
      REGION          = var.region_suffix
      SALT_PARAM_NAME = var.salt_param_name
    }
  }

  depends_on = [
    aws_iam_role_policy.mpi_registrar_lambda_policy,
    aws_cloudwatch_log_group.mpi_registrar_lambda_log_group
  ]
}

resource "aws_lambda_event_source_mapping" "mpi_registrar_trigger" {
  event_source_arn  = var.dynamodbstream_arn
  function_name     = aws_lambda_function.mpi_registrar_lambda.arn
  starting_position = "LATEST"
}