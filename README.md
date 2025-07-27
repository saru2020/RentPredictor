# ML Crash Course: House Rent Prediction

A complete MLOps pipeline for house rent prediction using Apache Spark, Airflow, and modern cloud-native technologies.

## 🚀 Quick Start Guide

### Prerequisites
- Docker and Docker Compose installed
- Python 3.8+ (for data upload script)

### Complete Setup Steps

#### 1. **Start All Services**
```bash
docker compose up -d
```

**This starts:**
- **MinIO** (S3-compatible storage) on port 9000
- **Spark** (data processing) on port 8080  
- **Airflow** (workflow orchestration) on port 8081
- **Model API** (prediction service) on port 5001

#### 2. **Upload Dataset to MinIO**
```bash
export S3_ENDPOINT_URL=http://localhost:9000
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
export S3_BUCKET=ml-crash-course-data
export S3_KEY=House_Rent_Dataset.csv
python upload_data_to_s3.py
```

#### 3. **Run ML Training Job**
```bash
docker compose up -d #note: Spark container: restarting the container itself would trigger the job, so the below trigger may not be required at all since the docker-compose.yml would build the image defined in Dockerfile inside `spark_jobs` folder
export S3_ENDPOINT_URL=http://localhost:9000
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
export S3_BUCKET=ml-crash-course-data
export S3_KEY=House_Rent_Dataset.csv
export MODEL_PATH=s3a://ml-crash-course-data/model
docker compose exec spark spark-submit --packages org.apache.hadoop:hadoop-aws:3.3.2 /opt/bitnami/spark_jobs/preprocess_and_train.py
```

#### 4. **Test the Model API**
```bash
# Health check
curl http://localhost:5001/health

# Make a prediction
curl -X POST http://localhost:5001/predict \
  -H "Content-Type: application/json" \
  -d '[{"BHK": 2, "Size": 1000, "Bathroom": 2, "Area Locality": "Some Area", "City": "Mumbai", "Furnishing Status": "Furnished", "Tenant Preferred": "Family", "Point of Contact": "Contact Owner"}]'
```

#### 5. **(Optional) Use Airflow for Orchestration**
[note: this approach is not working in local due to the error for calling docker inside docker container, so use Step 3 to trigger the docker container manually to train the model]
- Access Airflow UI at http://localhost:8081
- **Credentials:** 
  - Username: `admin`
  - Password: `admin`
- Find the `ml_pipeline` DAG and trigger it 
- This will run the same Spark job through Airflow orchestration

### 📊 **Service Access URLs**

| Service | URL | Purpose |
|---------|-----|---------|
| **MinIO Console** | http://localhost:9001 | S3-compatible storage management |
| **Spark UI** | http://localhost:8080 | Monitor Spark jobs |
| **Airflow UI** | http://localhost:8081 | Workflow orchestration |
| **Model API** | http://localhost:5001 | REST API for predictions |

### 🔑 **Default Credentials**

| Service | Username | Password |
|---------|----------|----------|
| **MinIO** | `minioadmin` | `minioadmin` |
| **Airflow** | `admin` | `admin` |

### 📝 **Complete Manual Workflow**

Here's the **exact sequence** of manual actions needed to run the full pipeline:

1. **Start Services:** `docker compose up -d`
2. **Upload Data:** Run the upload script with environment variables
3. **Train Model:** Execute the Spark training job
4. **Test API:** Make prediction requests to verify everything works
5. **(Optional) Orchestrate:** Use Airflow UI to trigger the pipeline

### 🎯 **Expected Results**

After completing all steps, you should see:
- ✅ Dataset uploaded to MinIO
- ✅ Model trained and saved (RMSE: ~44,905, R²: ~0.466)
- ✅ API returning predictions like: `[{"prediction": 43326.52}]`
- ✅ All services running and accessible via their respective URLs

## 🔄 **What Each Step Does**

### **Step 1: Start Services**
- **Docker Compose** starts all containers with proper networking
- **MinIO** provides S3-compatible storage locally
- **Spark** is ready for data processing
- **Airflow** is ready for workflow orchestration
- **Model API** is ready to serve predictions

### **Step 2: Upload Data**
- **upload_data_to_s3.py** checks if data exists in MinIO
- If not found, uploads the CSV dataset
- Data becomes available for Spark processing

### **Step 3: Train Model**
- **Spark job** reads CSV from MinIO
- **Feature Engineering:** Converts text to numbers, combines features
- **Model Training:** Random Forest learns from 80% of data
- **Model Saving:** Trained model stored in MinIO
- **Evaluation:** Performance metrics displayed

### **Step 4: Test API**
- **Health Check:** Verifies API is running
- **Prediction:** Sends house data, gets rent prediction
- **Validation:** Confirms end-to-end pipeline works

### **Step 5: Airflow (Optional)**
- **DAG Trigger:** Runs the same Spark job via Airflow
- **Monitoring:** Track job execution in Airflow UI
- **Automation:** Can schedule regular model retraining

## 🚀 **CI/CD (AWS Deployment)**

- On push to `main` or `data`, the workflow `.github/workflows/data-upload.yml` will upload the dataset to S3 if not already present.
- Infrastructure provisioning and deployment are automated via GitHub Actions.