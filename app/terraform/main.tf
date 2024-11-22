provider "aws" {
  region  = "ap-south-1"  # Replace with your region
  profile = "cli-user"      # Replace with your profile name
}

resource "aws_iam_role" "lambda_role" {
  name               = "lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_ecr_repository" "my_repo" {
  name = "s3-to-rds-or-glue-repo"
}

resource "aws_lambda_function" "s3_to_rds_or_glue" {
  function_name = "s3-to-rds-or-glue"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.my_repo.repository_url}:latest"
  role          = aws_iam_role.lambda_role.arn
}
