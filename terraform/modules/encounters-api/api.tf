resource "aws_apigatewayv2_api" "encounters_api" {
  name          = "encounters-http-api_${var.region_suffix}"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "encounters_api_stage" {
  api_id      = aws_apigatewayv2_api.encounters_api.id
  name        = "$default"
  auto_deploy = true
}

# read lambda api:
resource "aws_apigatewayv2_integration" "encounters_api_lambda_integration" {
  api_id             = aws_apigatewayv2_api.encounters_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.encounters_read_lambda.arn
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "encounters_api_route" {
  api_id    = aws_apigatewayv2_api.encounters_api.id
  route_key = "GET /patients/{patient_id}/encounters"
  authorization_type = "JWT"
  authorizer_id = aws_apigatewayv2_authorizer.encounters_api_cognito_authorizer.id
  target    = "integrations/${aws_apigatewayv2_integration.encounters_api_lambda_integration.id}"
}

resource "aws_lambda_permission" "apigw_lambda_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.encounters_read_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.encounters_api.execution_arn}/*/*"
}

# write lambda api:
resource "aws_apigatewayv2_integration" "encounters_write_api_lambda_integration" {
  api_id             = aws_apigatewayv2_api.encounters_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.encounters_write_lambda.arn
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "encounters_write_api_route" {
  api_id    = aws_apigatewayv2_api.encounters_api.id
  route_key = "POST /encounters"
  authorization_type = "JWT"
  authorizer_id = aws_apigatewayv2_authorizer.encounters_api_cognito_authorizer.id
  target    = "integrations/${aws_apigatewayv2_integration.encounters_write_api_lambda_integration.id}"
}

resource "aws_lambda_permission" "apigw_write_lambda_permission" {
  statement_id  = "AllowAPIGatewayInvokeWrite"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.encounters_write_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.encounters_api.execution_arn}/*/*"
}

# update lambda api:
resource "aws_apigatewayv2_integration" "encounters_update_api_lambda_integration" {
  api_id             = aws_apigatewayv2_api.encounters_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.encounters_update_lambda.arn
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "encounters_update_api_route" {
  api_id    = aws_apigatewayv2_api.encounters_api.id
  route_key = "PATCH /encounters"
  authorization_type = "JWT"
  authorizer_id = aws_apigatewayv2_authorizer.encounters_api_cognito_authorizer.id
  target    = "integrations/${aws_apigatewayv2_integration.encounters_update_api_lambda_integration.id}"
}

resource "aws_lambda_permission" "apigw_update_lambda_permission" {
  statement_id  = "AllowAPIGatewayInvokeUpdate"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.encounters_update_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.encounters_api.execution_arn}/*/*"
}


# cognito Authoriser:
resource "aws_apigatewayv2_authorizer" "encounters_api_cognito_authorizer" {
  api_id = aws_apigatewayv2_api.encounters_api.id
  name   = "encounters-api-cognito-authorizer"
  authorizer_type = "JWT"
  identity_sources = ["$request.header.Authorization"]
  jwt_configuration {
    audience = [var.cognito_client_id]
    issuer   = "https://cognito-idp.eu-west-2.amazonaws.com/${var.cognito_user_pool_id}"
  }
}