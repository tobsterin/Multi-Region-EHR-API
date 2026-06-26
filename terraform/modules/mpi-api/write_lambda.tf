data "archive_file" "mpi_write_lambda_archive" {
  type = "zip"
  source_file = "${path.module}/src/write_mpi.py"
  output_path = "${path.module}/dist/write_mpi.zip"
}

data "aws_ssm_parameter" "salt" {
  name = "/mpi/salt"
}

resource "aws_lambda_function" "mpi_write_lambda" {
  function_name    = "mpi-write-lambda-${var.region_suffix}"
  role             = aws_iam_role.mpi_write_lambda_role.arn
  handler          = "write_mpi.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.mpi_write_lambda_archive.output_path
  source_code_hash = data.archive_file.mpi_write_lambda_archive.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = "mpi_global_table"
      SALT       = data.aws_ssm_parameter.salt.value
    }
  }

  depends_on = [
    aws_iam_role_policy.mpi_write_lambda_policy,
    aws_cloudwatch_log_group.mpi_write_lambda_log_group
  ]
}