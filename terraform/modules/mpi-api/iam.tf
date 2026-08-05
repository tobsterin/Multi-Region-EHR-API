# Account
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

data "aws_kms_key" "ssm_key" {
  key_id = "alias/aws/ssm"
}

# read lambda role and policy:
resource "aws_iam_role" "mpi_read_lambda_role" {
  name = "mpi_read_lambda_role-${var.region_suffix}"
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

resource "aws_iam_role_policy" "mpi_read_lambda_policy" {
  name = "mpi_read_lambda_policy-${var.region_suffix}"
  role = aws_iam_role.mpi_read_lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ssm:GetParameter"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/mpi/salt"
        ]
      },
      {
        Action = [
          "kms:Decrypt"
        ]
        Effect   = "Allow"
        Resource = [data.aws_kms_key.ssm_key.arn]
      },
      {
        Action = [
          "dynamodb:Query"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:dynamodb:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:table/mpi_global_table",
          "arn:aws:dynamodb:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:table/mpi_global_table/index/*"
        ]
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "${aws_cloudwatch_log_group.mpi_read_lambda_log_group.arn}:*"
      }
    ]
  })
}