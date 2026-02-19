resource "aws_cognito_user_pool" "this" {
  name                       = "${var.project}-${var.env}-user-pool"
  auto_verified_attributes   = ["email"]
  username_attributes        = ["email"]
  mfa_configuration          = "OFF"

  admin_create_user_config {
    allow_admin_create_user_only = true
  }

  schema {
    name                = "role"
    attribute_data_type = "String"
    mutable             = true
    required            = false
  }

  tags = var.tags
}

resource "aws_cognito_user_pool_client" "this" {
  name                          = "${var.project}-${var.env}-client"
  user_pool_id                  = aws_cognito_user_pool.this.id
  explicit_auth_flows           = ["ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH", "ALLOW_CUSTOM_AUTH"]
  prevent_user_existence_errors = "ENABLED"
  generate_secret               = false
}
