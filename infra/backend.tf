terraform {
  backend "s3" {
    bucket = "ml-crash-course-terraform-state"
    key    = "infrastructure/terraform.tfstate"
    # region will be set via -backend-config during init
  }
} 