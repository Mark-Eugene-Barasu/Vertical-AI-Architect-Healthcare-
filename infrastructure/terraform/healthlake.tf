resource "aws_healthlake_fhir_datastore" "medimind" {
  datastore_name       = "medimind-fhir"
  datastore_type_version = "R4"

  sse_configuration {
    kms_encryption_config {
      cmk_type = "AWS_OWNED_KMS_KEY"
    }
  }

  tags = {
    Project     = "MediMind AI"
    Environment = "production"
    Compliance  = "HIPAA"
  }
}

output "healthlake_endpoint" {
  value       = aws_healthlake_fhir_datastore.medimind.datastore_endpoint
  description = "Amazon HealthLake FHIR endpoint — set as HEALTHLAKE_ENDPOINT env var"
}

output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.clinicians.id
}

output "cognito_client_id" {
  value = aws_cognito_user_pool_client.app.id
}

output "audio_bucket_name" {
  value = aws_s3_bucket.audio.bucket
}
