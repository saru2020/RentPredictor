#!/bin/bash

# Spark Job Trigger Script
# This script triggers the ML Spark job to preprocess data and train the model

set -e

echo "🔥 Triggering Spark Job..."
echo "=========================="

# Get AWS account ID and region from environment or set defaults
AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID:-$(aws sts get-caller-identity --query Account --output text)}
AWS_REGION=${AWS_REGION:-us-east-2}

echo "📊 Configuration:"
echo "  AWS Account ID: $AWS_ACCOUNT_ID"
echo "  AWS Region: $AWS_REGION"
echo "  S3 Bucket: ml-crash-course-data"
echo "  Dataset: House_Rent_Dataset.csv"

# Create the Spark job with proper image URI and AWS credentials
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: ml-spark-job-$(date +%s)
  labels:
    app: ml-spark-job
spec:
  template:
    metadata:
      labels:
        app: ml-spark-job
    spec:
      serviceAccountName: spark-sa
      containers:
      - name: spark-job
        image: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/ml-crash-course-spark:latest
        env:
        - name: S3_BUCKET
          value: "ml-crash-course-data"
        - name: S3_KEY
          value: "House_Rent_Dataset.csv"
        - name: AWS_REGION
          value: "$AWS_REGION"
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: access-key-id
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: secret-access-key
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      restartPolicy: Never
  backoffLimit: 3
EOF

echo ""
echo "✅ Spark job created successfully!"
echo ""
echo "📋 Monitoring Commands:"
echo "  # Check job status"
echo "  kubectl get jobs"
echo ""
echo "  # View job logs"
echo "  kubectl logs job/ml-spark-job-$(date +%s)"
echo ""
echo "  # Monitor job progress"
echo "  kubectl describe job ml-spark-job-$(date +%s)"
echo ""
echo "  # Check pod status"
echo "  kubectl get pods -l app=ml-spark-job" 