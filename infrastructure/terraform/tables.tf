# ── Usage Tracking Table ──────────────────────────────────────────────────────
resource "aws_dynamodb_table" "usage" {
  name         = "medimind-usage"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "org_id"
  range_key    = "month"

  attribute {
    name = "org_id"
    type = "S"
  }

  attribute {
    name = "month"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }
}

# ── Organizations Table ───────────────────────────────────────────────────────
resource "aws_dynamodb_table" "organizations" {
  name         = "medimind-organizations"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "org_id"

  attribute {
    name = "org_id"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }

  point_in_time_recovery {
    enabled = true
  }
}
