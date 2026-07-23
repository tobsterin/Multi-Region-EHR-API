# read lambda role and policy:
resource "aws_iam_role" "observations_read_lambda_role" {
  name = "observations-read-lambda-role-${var.region_suffix}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
  
}

resource "aws_iam_role_policy" "observations_read_lambda_policy" {
  name = "observations-read-lambda-policy-${var.region_suffix}"
  role = aws_iam_role.observations_read_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:GetItem",
          "dynamodb:Query"
        ]
        Effect   = "Allow"
        Resource = var.table_arn
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "${aws_cloudwatch_log_group.observations_read_lambda_log_group.arn}:*"
      }
    ]
  })
}


# write lambda role and policy:
resource "aws_iam_role" "observations_write_lambda_role" {
  name = "observations-write-lambda-role-${var.region_suffix}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
  
}

resource "aws_iam_role_policy" "observations_write_lambda_policy" {
  name = "observations-write-lambda-policy-${var.region_suffix}"
  role = aws_iam_role.observations_write_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:PutItem"
        ]
        Effect   = "Allow"
        Resource = var.table_arn
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "${aws_cloudwatch_log_group.observations_write_lambda_log_group.arn}:*"
      }
    ]
  })
}


# update lambda role and policy:
resource "aws_iam_role" "observations_update_lambda_role" {
  name = "observations-update-lambda-role-${var.region_suffix}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
  
}

resource "aws_iam_role_policy" "observations_update_lambda_policy" {
  name = "observations-update-lambda-policy-${var.region_suffix}"
  role = aws_iam_role.observations_update_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:UpdateItem"
        ]
        Effect   = "Allow"
        Resource = var.table_arn
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "${aws_cloudwatch_log_group.observations_update_lambda_log_group.arn}:*"
      }
    ]
  })
}