from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import subprocess
import time
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'ml_pipeline',
    default_args=default_args,
    description='ML pipeline for house rent prediction',
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
)

def run_spark_job():
    """Run the Spark training job with proper error handling"""
    try:
        print("Starting Spark training job...")
        
        # Check if Spark container is running, start if needed
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=ml_crash_course-spark-1", "--format", "table", "{{.Names}}"],
                capture_output=True, text=True, check=True
            )
            if "ml_crash_course-spark-1" not in result.stdout:
                print("Spark container not running, attempting to start it...")
                # Try different ways to start the container
                try:
                    # Try docker compose (if available)
                    subprocess.run(["docker", "compose", "up", "-d", "spark"], check=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    try:
                        # Try docker-compose (if available)
                        subprocess.run(["docker-compose", "up", "-d", "spark"], check=True)
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        print("docker-compose not available, trying direct docker commands...")
                        # Try to start the container directly
                        subprocess.run(["docker", "start", "ml_crash_course-spark-1"], check=True)
                
                time.sleep(5)  # Wait for container to be ready
            else:
                print("Spark container is already running")
        except subprocess.CalledProcessError as e:
            print(f"Error checking Spark container: {e}")
            print("Assuming Spark container is running and proceeding...")
        
        # Run the Spark job
        print("Executing Spark training job...")
        result = subprocess.run([
            "docker", "exec", "ml_crash_course-spark-1",
            "spark-submit", "--packages", "org.apache.hadoop:hadoop-aws:3.3.2",
            "/opt/bitnami/spark_jobs/preprocess_and_train.py"
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        print(f"Spark job stdout: {result.stdout}")
        if result.stderr:
            print(f"Spark job stderr: {result.stderr}")
        
        if result.returncode == 0:
            print("✅ Spark job completed successfully!")
            return True
        else:
            print(f"❌ Spark job failed with exit code {result.returncode}")
            raise Exception(f"Spark job failed with exit code {result.returncode}")
            
    except subprocess.TimeoutExpired:
        print("❌ Spark job timed out after 5 minutes")
        raise Exception("Spark job timed out after 5 minutes")
    except Exception as e:
        print(f"❌ Error running Spark job: {e}")
        raise

spark_job = PythonOperator(
    task_id='preprocess_and_train',
    python_callable=run_spark_job,
    dag=dag,
) 