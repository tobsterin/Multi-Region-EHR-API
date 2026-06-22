data "archive_file" "patient_read_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/src/read_patient.py"
  output_path = "${path.module}/dist/read_patient.zip"
}

resource "aws_lambda_function" "patient_read_lambda" {
  function_name    = "patient-read-lambda-${var.region_suffix}"
  role             = aws_iam_role.patient_read_lambda_role.arn
  handler          = "read_patient.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.patient_read_lambda_zip.output_path
  source_code_hash = data.archive_file.patient_read_lambda_zip.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = var.table_name
    }
  }

  depends_on = [
    aws_iam_role_policy.patient_read_lambda_policy,
    aws_cloudwatch_log_group.patient_read_lambda_log_group
  ]
  
}
