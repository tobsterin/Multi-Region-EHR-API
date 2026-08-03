data "archive_file" "patient_update_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/src/update_patient.py"
  output_path = "${path.module}/dist/update_patient.zip"
}

resource "aws_lambda_function" "patient_update_lambda" {
  function_name    = "patient-update-lambda-${var.region_suffix}"
  role             = aws_iam_role.patient_update_lambda_role.arn
  handler          = "update_patient.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.patient_update_lambda_zip.output_path
  source_code_hash = data.archive_file.patient_update_lambda_zip.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = var.table_name
    }
  }

  depends_on = [
    aws_iam_role_policy.patient_update_lambda_policy,
    aws_cloudwatch_log_group.patient_update_lambda_log_group
  ]

}