provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "ml_data" {
  bucket = var.s3_bucket_name
  force_destroy = true
}

module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  cluster_name    = var.eks_cluster_name
  cluster_version = "1.29"
  subnets         = var.eks_subnets
  vpc_id          = var.eks_vpc_id
  node_groups = {
    default = {
      desired_capacity = 2
      max_capacity     = 3
      min_capacity     = 1
      instance_type    = "t3.medium"
    }
  }
}

variable "aws_region" {}
variable "s3_bucket_name" {}
variable "eks_cluster_name" {}
variable "eks_subnets" { type = list(string) }
variable "eks_vpc_id" {}
