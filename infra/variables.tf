variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "s3_bucket_name" {
  description = "S3 bucket for ML data"
  type        = string
  default     = "ml-crash-course-data"
}

variable "eks_cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "ml-crash-course-cluster"
}
