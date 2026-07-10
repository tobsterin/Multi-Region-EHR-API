resource "aws_cognito_user_pool" "cognito_user_pool" {
  name = "ehr-user-pool"
  password_policy {
    minimum_length    = 15
    require_uppercase = true
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
  }
}

resource "aws_cognito_user_pool_client" "cognito_user_pool_client" {
  name         = "ehr-user-pool-client"
  user_pool_id = aws_cognito_user_pool.cognito_user_pool.id
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]
}