resource "aws_apigatewayv2_api" "mpi-api" {
  name          = "mpi-api-${var.region_suffix}"
  protocol_type = "HTTP"
  
}

resource "aws_apigatewayv2_stage" "mpi_api_stage" {
  api_id      = aws_apigatewayv2_api.mpi-api.id
  name        = "$default"
  auto_deploy = true
}

# read lambda api:
resource "aws_apigatewayv2_integration" "mpi_api_lambda_integration" {
  api_id             = aws_apigatewayv2_api.mpi-api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.mpi_read_lambda.arn
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "mpi_api_route" {
  api_id    = aws_apigatewayv2_api.mpi-api.id
  route_key = "GET /mpi"
  target    = "integrations/${aws_apigatewayv2_integration.mpi_api_lambda_integration.id}"
}

resource "aws_lambda_permission" "mpi_api_lambda_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.mpi_read_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.mpi-api.execution_arn}/*/*"
}