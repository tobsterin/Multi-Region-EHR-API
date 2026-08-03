resource "aws_apigatewayv2_api" "patient_api" {
  name          = "patient-http-api_${var.region_suffix}"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "patient_api_stage" {
  api_id      = aws_apigatewayv2_api.patient_api.id
  name        = "$default"
  auto_deploy = true
}

# read lambda api:
resource "aws_apigatewayv2_integration" "patient_api_lambda_integration" {
  api_id             = aws_apigatewayv2_api.patient_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.patient_read_lambda.arn
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "patient_api_route" {
  api_id             = aws_apigatewayv2_api.patient_api.id
  route_key          = "GET /patients/{patient_id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.patient_api_cognito_authorizer.id
  target             = "integrations/${aws_apigatewayv2_integration.patient_api_lambda_integration.id}"
}

resource "aws_lambda_permission" "apigw_lambda_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.patient_read_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.patient_api.execution_arn}/*/*"
}

# write lambda api:
resource "aws_apigatewayv2_integration" "patient_write_api_lambda_integration" {
  api_id             = aws_apigatewayv2_api.patient_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.patient_write_lambda.arn
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "patient_write_api_route" {
  api_id             = aws_apigatewayv2_api.patient_api.id
  route_key          = "POST /patients"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.patient_api_cognito_authorizer.id
  target             = "integrations/${aws_apigatewayv2_integration.patient_write_api_lambda_integration.id}"
}

resource "aws_lambda_permission" "apigw_write_lambda_permission" {
  statement_id  = "AllowAPIGatewayInvokeWrite"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.patient_write_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.patient_api.execution_arn}/*/*"
}

# update lambda api:
resource "aws_apigatewayv2_integration" "patient_update_api_lambda_integration" {
  api_id             = aws_apigatewayv2_api.patient_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.patient_update_lambda.arn
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "patient_update_api_route" {
  api_id             = aws_apigatewayv2_api.patient_api.id
  route_key          = "PATCH /patients/{patient_id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.patient_api_cognito_authorizer.id
  target             = "integrations/${aws_apigatewayv2_integration.patient_update_api_lambda_integration.id}"
}

resource "aws_lambda_permission" "apigw_update_lambda_permission" {
  statement_id  = "AllowAPIGatewayInvokeUpdate"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.patient_update_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.patient_api.execution_arn}/*/*"
}


# cognito Authoriser:
resource "aws_apigatewayv2_authorizer" "patient_api_cognito_authorizer" {
  api_id           = aws_apigatewayv2_api.patient_api.id
  name             = "patient-api-cognito-authorizer"
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  jwt_configuration {
    audience = [var.cognito_client_id]
    issuer   = "https://cognito-idp.eu-west-2.amazonaws.com/${var.cognito_user_pool_id}"
  }
}