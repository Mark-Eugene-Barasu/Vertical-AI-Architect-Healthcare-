variable "aws_region" {
  default = "us-east-1"
}

variable "account_id" {
  description = "AWS Account ID"
  type        = string
}

variable "domain_name" {
  description = "Your app domain e.g. app.medimind.ai"
  type        = string
}

variable "acm_certificate_arn" {
  description = "ACM certificate ARN for HTTPS (must be in us-east-1 for CloudFront)"
  type        = string
}

variable "alert_email" {
  description = "Email address to receive critical clinical alerts"
  type        = string
}
