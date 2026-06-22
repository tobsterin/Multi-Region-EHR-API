resource "aws_apigatewayv2_api" "patient_api" {
  name          = "patient-http-api_${var.region_suffix}"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "patient_api_stage" {
  api_id      = aws_apigatewayv2_api.patient_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "patient_api_lambda_integration" {
  api_id             = aws_apigatewayv2_api.patient_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.patient_read_lambda.arn
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "patient_api_route" {
  api_id    = aws_apigatewayv2_api.patient_api.id
  route_key = "GET /patients/{patient_id}"
  target    = "integrations/${aws_apigatewayv2_integration.patient_api_lambda_integration.id}"
}

resource "aws_lambda_permission" "apigw_lambda_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.patient_read_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.patient_api.execution_arn}/*/*"
}