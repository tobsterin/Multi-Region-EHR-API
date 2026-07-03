# Account
data "aws_caller_identity" "current" {}

# Role + Policy
resource "aws_iam_role" "mpi_registrar_lambda_role" {
  name = "mpi_registrar_lambda_role-${var.region_suffix}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "mpi_registrar_lambda_policy" {
  name = "mpi_registrar_lambda_policy-${var.region_suffix}"
  role = aws_iam_role.mpi_registrar_lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:PutItem"
        ]
        Effect   = "Allow"
        Resource = [
          "arn:aws:dynamodb:eu-west-2:${data.aws_caller_identity.current.account_id}:table/mpi_global_table",
          "arn:aws:dynamodb:eu-central-1:${data.aws_caller_identity.current.account_id}:table/mpi_global_table",
          "arn:aws:dynamodb:eu-west-3:${data.aws_caller_identity.current.account_id}:table/mpi_global_table"
        ]
      },
      {
        Action = [
          "dynamodb:Query"
        ]
        Effect   = "Allow"
        Resource = [
          "arn:aws:dynamodb:eu-west-2:${data.aws_caller_identity.current.account_id}:table/mpi_global_table",
          "arn:aws:dynamodb:eu-central-1:${data.aws_caller_identity.current.account_id}:table/mpi_global_table",
          "arn:aws:dynamodb:eu-west-3:${data.aws_caller_identity.current.account_id}:table/mpi_global_table",
          "arn:aws:dynamodb:eu-west-2:${data.aws_caller_identity.current.account_id}:table/mpi_global_table/index/*",
          "arn:aws:dynamodb:eu-central-1:${data.aws_caller_identity.current.account_id}:table/mpi_global_table/index/*",
          "arn:aws:dynamodb:eu-west-3:${data.aws_caller_identity.current.account_id}:table/mpi_global_table/index/*",

        ]
      },
      {
        Action = [
          "dynamodb:GetRecords",
          "dynamodb:GetShardIterator",
          "dynamodb:DescribeStream",
          "dynamodb:ListStreams"
        ]
        Effect = "Allow"
        Resource = var.dynamodbstream_arn
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "${aws_cloudwatch_log_group.mpi_registrar_lambda_log_group.arn}:*"
      }
    ]
  })
}