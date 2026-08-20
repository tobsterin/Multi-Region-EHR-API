data "archive_file" "helpers_layer_zip" {
  type        = "zip"
  source_dir  = "${path.module}/src"
  output_path = "${path.module}/dist/helpers_layer.zip"
}

resource "aws_lambda_layer_version" "helpers" {
  layer_name          = "${var.layer_name}-${var.region_suffix}"
  filename            = data.archive_file.helpers_layer_zip.output_path
  source_code_hash    = data.archive_file.helpers_layer_zip.output_base64sha256
  compatible_runtimes = ["python3.12"]
}
