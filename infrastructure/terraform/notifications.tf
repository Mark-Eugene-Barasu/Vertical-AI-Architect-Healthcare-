# ── SES Email Identity ────────────────────────────────────────────────────────
resource "aws_ses_email_identity" "noreply" {
  email = "noreply@medimind.ai"
}

# ── Lambda IAM Role ───────────────────────────────────────────────────────────
resource "aws_iam_role" "notifications_lambda" {
  name = "medimind-notifications-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "notifications_lambda_policy" {
  name = "medimind-notifications-lambda-policy"
  role = aws_iam_role.notifications_lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "ses:SendEmail",
        "dynamodb:Scan",
        "dynamodb:GetItem",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ]
      Resource = "*"
    }]
  })
}

# ── Lambda Function ───────────────────────────────────────────────────────────
resource "aws_lambda_function" "notifications" {
  function_name    = "medimind-notifications"
  role             = aws_iam_role.notifications_lambda.arn
  handler          = "services/notifications/scheduler.lambda_handler"
  runtime          = "python3.11"
  timeout          = 300
  filename         = "notifications_lambda.zip"
  source_code_hash = filebase64sha256("notifications_lambda.zip")

  environment {
    variables = {
      AWS_REGION     = var.aws_region
      SES_FROM_EMAIL = "noreply@medimind.ai"
    }
  }
}

# ── EventBridge Rules ─────────────────────────────────────────────────────────
resource "aws_cloudwatch_event_rule" "daily" {
  name                = "medimind-daily-notifications"
  schedule_expression = "cron(0 8 * * ? *)"
}

resource "aws_cloudwatch_event_rule" "monthly" {
  name                = "medimind-monthly-reports"
  schedule_expression = "cron(0 9 1 * ? *)"
}

resource "aws_cloudwatch_event_target" "daily" {
  rule      = aws_cloudwatch_event_rule.daily.name
  target_id = "DailyNotifications"
  arn       = aws_lambda_function.notifications.arn
  input     = jsonencode({ rule = "daily" })
}

resource "aws_cloudwatch_event_target" "monthly" {
  rule      = aws_cloudwatch_event_rule.monthly.name
  target_id = "MonthlyReports"
  arn       = aws_lambda_function.notifications.arn
  input     = jsonencode({ rule = "monthly" })
}

resource "aws_lambda_permission" "daily" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.notifications.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily.arn
}

resource "aws_lambda_permission" "monthly" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.notifications.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.monthly.arn
}
