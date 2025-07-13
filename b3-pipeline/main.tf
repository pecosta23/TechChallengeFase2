provider "aws" {
  region = "us-east-1"
}

# Bucket S3
resource "aws_s3_bucket" "b3_raw_data" {
  bucket        = var.s3_b3_raw_bucket_name
  force_destroy = true
}

# Bucket S3
resource "aws_s3_bucket" "b3_refined_data" {
  bucket        = var.s3_b3_raw_bucket_name
  force_destroy = true
}


# Lambda function to trigger Glue job
resource "aws_s3_bucket_notification" "notify_lambda" {
  bucket = aws_s3_bucket.b3_raw_data.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.trigger_glue.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "b3/"
    filter_suffix       = ".parquet"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}

resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_trigger_glue"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "invoke_glue_policy" {
  name = "invoke-glue"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = "glue:StartJobRun",
        Resource = "*"
      }
    ]
  })
}

resource "aws_lambda_function" "trigger_glue" {
  filename         = "files/trigger_glue.zip" # contém handler.py
  function_name    = "trigger_glue_job"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = filebase64sha256("files/trigger_glue.zip")
  timeout          = 30
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
