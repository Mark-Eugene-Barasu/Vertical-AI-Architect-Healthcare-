terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  backend "s3" {
    bucket = "medimind-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 bucket for audio files (HIPAA: encrypted)
resource "aws_s3_bucket" "audio" {
  bucket = "medimind-audio-${var.account_id}"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "audio" {
  bucket = aws_s3_bucket.audio.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "audio" {
  bucket                  = aws_s3_bucket.audio.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDB for clinical notes
resource "aws_dynamodb_table" "clinical_notes" {
  name         = "medimind-clinical-notes"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "patient_id"
  range_key    = "note_id"

  attribute {
    name = "patient_id"
    type = "S"
  }
  attribute {
    name = "note_id"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }

  point_in_time_recovery {
    enabled = true
  }
}

# Cognito User Pool for clinician auth
resource "aws_cognito_user_pool" "clinicians" {
  name = "medimind-clinicians"

  password_policy {
    minimum_length    = 12
    require_uppercase = true
    require_numbers   = true
    require_symbols   = true
  }

  mfa_configuration = "ON"

  software_token_mfa_configuration {
    enabled = true
  }
}

resource "aws_cognito_user_pool_client" "app" {
  name         = "medimind-app-client"
  user_pool_id = aws_cognito_user_pool.clinicians.id
  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]
}

# CloudTrail for HIPAA audit logging
resource "aws_cloudtrail" "audit" {
  name                          = "medimind-audit-trail"
  s3_bucket_name                = aws_s3_bucket.audio.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
}
