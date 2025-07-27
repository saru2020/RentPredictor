from flask import Flask, request, jsonify
import os
from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel
import pandas as pd

app = Flask(__name__)

MODEL_PATH = os.environ.get('MODEL_PATH', 's3a://ml-crash-course-data/model')
S3_ENDPOINT = os.environ.get('S3_ENDPOINT_URL')
S3_BUCKET = os.environ.get('S3_BUCKET', 'ml-crash-course-data')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'minioadmin')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'minioadmin')

spark = None
model = None

def get_spark():
    global spark
    if spark is None:
        # Configure Spark for local mode with Bitnami image
        builder = SparkSession.builder \
            .appName('ModelAPI') \
            .master('local[*]') \
            .config('spark.driver.host', 'localhost') \
            .config('spark.driver.bindAddress', '127.0.0.1') \
            .config('spark.sql.adaptive.enabled', 'false') \
            .config('spark.sql.adaptive.coalescePartitions.enabled', 'false') \
            .config('spark.driver.extraJavaOptions', '-Djava.net.preferIPv4Stack=true') \
            .config('spark.executor.extraJavaOptions', '-Djava.net.preferIPv4Stack=true') \
            .config('spark.driver.memory', '1g') \
            .config('spark.executor.memory', '1g')
        
        spark = builder.getOrCreate()
        
        if S3_ENDPOINT:
            spark._jsc.hadoopConfiguration().set('fs.s3a.endpoint', S3_ENDPOINT)
            spark._jsc.hadoopConfiguration().set('fs.s3a.access.key', AWS_ACCESS_KEY_ID)
            spark._jsc.hadoopConfiguration().set('fs.s3a.secret.key', AWS_SECRET_ACCESS_KEY)
            spark._jsc.hadoopConfiguration().set('fs.s3a.path.style.access', 'true')
            spark._jsc.hadoopConfiguration().set('fs.s3a.impl', 'org.apache.hadoop.fs.s3a.S3AFileSystem')
    return spark

def get_model():
    global model
    if model is None:
        spark = get_spark()
        model = PipelineModel.load(MODEL_PATH)
    return model

@app.route('/')
def index():
    return 'Model API is running!'

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Expecting a list of dicts
        if not isinstance(data, list):
            data = [data]
        
        df = pd.DataFrame(data)
        spark_df = get_spark().createDataFrame(df)
        model = get_model()
        preds = model.transform(spark_df)
        result = preds.select('prediction').toPandas().to_dict(orient='records')
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'message': 'Model API is running'})

@app.route('/test-spark', methods=['GET'])
def test_spark():
    try:
        spark = get_spark()
        # Create a simple test DataFrame
        test_data = [{'test': 1}, {'test': 2}]
        df = spark.createDataFrame(test_data)
        count = df.count()
        return jsonify({'status': 'success', 'message': f'Spark is working! DataFrame count: {count}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Spark test failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 