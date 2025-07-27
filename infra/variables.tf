variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
}

variable "s3_bucket_name" {
  description = "S3 bucket for ML data"
  type        = string
}

variable "eks_cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "eks_subnets" {
  description = "Subnets for EKS nodes"
  type        = list(string)
}

variable "eks_vpc_id" {
  description = "VPC ID for EKS"
  type        = string
}
