# ── SNS Alert Topic ───────────────────────────────────────────────────────────
resource "aws_sns_topic" "alerts" {
  name              = "medimind-clinical-alerts"
  kms_master_key_id = "alias/aws/sns"
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# ── DynamoDB Timeline Table ───────────────────────────────────────────────────
resource "aws_dynamodb_table" "patient_timeline" {
  name         = "medimind-patient-timeline"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "patient_id"
  range_key    = "timestamp"

  attribute {
    name = "patient_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }

  point_in_time_recovery {
    enabled = true
  }
}

output "sns_alert_topic_arn" {
  value       = aws_sns_topic.alerts.arn
  description = "SNS topic ARN — set as SNS_ALERT_TOPIC_ARN env var"
}
