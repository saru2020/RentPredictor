terraform {
  backend "s3" {
    bucket = "ml-crash-course-terraform-state"
    key    = "infrastructure/terraform.tfstate"
    region = "us-east-2"  # This will be overridden by -backend-config
  }
} 