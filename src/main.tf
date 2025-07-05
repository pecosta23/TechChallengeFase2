provider "aws" {
  region = "us-east-1"
}

# Bucket S3
resource "aws_s3_bucket" "b3_data" {
  bucket        = var.s3_bucket_name
  force_destroy = true
}

# IAM para Lambda
resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_b3"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = { Service = "lambda.amazonaws.com" },
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_s3_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda Function
resource "aws_lambda_function" "extract_b3" {
  filename         = "files/lambda.zip"
  function_name    = "extract_b3_pregao"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "extract_b3.lambda_handler"
  runtime          = "python3.11"
  timeout          = 60
  source_code_hash = filebase64sha256("files/lambda.zip")
}

# EventBridge para agendamento
resource "aws_cloudwatch_event_rule" "daily_trigger" {
  name                = "trigger_b3_lambda_daily"
  schedule_expression = "rate(1 day)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.daily_trigger.name
  target_id = "lambda"
  arn       = aws_lambda_function.extract_b3.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.extract_b3.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_trigger.arn
}

# resource "aws_iam_role" "glue_role" {
#   name = "glue_b3_role"
#   assume_role_policy = jsonencode({
#     Version = "2012-10-17",
#     Statement = [{
#       Effect    = "Allow",
#       Principal = { Service = "glue.amazonaws.com" },
#       Action    = "sts:AssumeRole"
#     }]
#   })
# }

# resource "aws_iam_role_policy_attachment" "glue_s3_policy" {
#   role       = aws_iam_role.glue_role.name
#   policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
# }

# resource "aws_glue_job" "process_b3" {
#   name     = "glue-process-b3"
#   role_arn = aws_iam_role.glue_role.arn

#   command {
#     name            = "glueetl"
#     script_location = "s3://${var.s3_bucket_name}/scripts/glue_job.py"
#     python_version  = "3"
#   }

#   default_arguments = {
#     "--job-language" = "python"
#   }

#   max_retries       = 1
#   glue_version      = "3.0"
#   number_of_workers = 2
# }
