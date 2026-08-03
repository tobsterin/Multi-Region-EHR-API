data "archive_file" "mpi_read_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/src/read_mpi.py"
  output_path = "${path.module}/dist/read_mpi.zip"
}

data "aws_ssm_parameter" "salt" {
  name = "/mpi/salt"
}

resource "aws_lambda_function" "mpi_read_lambda" {
  function_name    = "mpi-read-lambda-${var.region_suffix}"
  role             = aws_iam_role.mpi_read_lambda_role.arn
  handler          = "read_mpi.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.mpi_read_lambda_zip.output_path
  source_code_hash = data.archive_file.mpi_read_lambda_zip.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = "mpi_global_table"
      SALT       = data.aws_ssm_parameter.salt.value
    }
  }

  depends_on = [
    aws_iam_role_policy.mpi_read_lambda_policy,
    aws_cloudwatch_log_group.mpi_read_lambda_log_group
  ]

}