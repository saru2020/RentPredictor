import os
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml import Pipeline

S3_ENDPOINT = os.environ.get('S3_ENDPOINT_URL')
S3_BUCKET = os.environ.get('S3_BUCKET', 'ml-crash-course-data')
S3_KEY = os.environ.get('S3_KEY', 'House_Rent_Dataset.csv')
MODEL_PATH = os.environ.get('MODEL_PATH', 's3a://ml-crash-course-data/model')

spark = SparkSession.builder.appName('HouseRentML').getOrCreate()

# Configure S3/MinIO
if S3_ENDPOINT:
    print(f"Configuring S3/MinIO with endpoint: {S3_ENDPOINT}")
    spark._jsc.hadoopConfiguration().set('fs.s3a.endpoint', S3_ENDPOINT)
    spark._jsc.hadoopConfiguration().set('fs.s3a.access.key', os.environ.get('AWS_ACCESS_KEY_ID', 'minioadmin'))
    spark._jsc.hadoopConfiguration().set('fs.s3a.secret.key', os.environ.get('AWS_SECRET_ACCESS_KEY', 'minioadmin'))
    spark._jsc.hadoopConfiguration().set('fs.s3a.path.style.access', 'true')
    spark._jsc.hadoopConfiguration().set('fs.s3a.impl', 'org.apache.hadoop.fs.s3a.S3AFileSystem')
    spark._jsc.hadoopConfiguration().set('fs.s3a.connection.ssl.enabled', 'false')
    spark._jsc.hadoopConfiguration().set('fs.s3a.aws.credentials.provider', 'org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider')
else:
    print("No S3_ENDPOINT_URL provided, using default S3 configuration")

# Read data
data_path = f's3a://{S3_BUCKET}/{S3_KEY}'
print(f"Reading data from: {data_path}")
df = spark.read.csv(data_path, header=True, inferSchema=True)
print(f"Data loaded successfully. Rows: {df.count()}, Columns: {len(df.columns)}")

# Show schema and sample data
print("Data schema:")
df.printSchema()
print("Sample data:")
df.show(5)

# Basic preprocessing: encode categoricals, assemble features
# Use only categorical columns with fewer unique values to avoid maxBins issue
categorical_cols = ['City', 'Furnishing Status', 'Tenant Preferred', 'Point of Contact']
# Skip 'Area Locality' as it has too many unique values (1951)

indexers = [StringIndexer(inputCol=col, outputCol=col+"_idx", handleInvalid='keep') for col in categorical_cols]
feature_cols = ['BHK', 'Size', 'Bathroom'] + [col+"_idx" for col in categorical_cols]
assembler = VectorAssembler(inputCols=feature_cols, outputCol='features')

# Use LinearRegression instead of RandomForest to avoid maxBins issue
from pyspark.ml.regression import LinearRegression
regressor = LinearRegression(featuresCol='features', labelCol='Rent')

pipeline = Pipeline(stages=indexers + [assembler, regressor])

# Train/test split
train, test = df.randomSplit([0.8, 0.2], seed=42)
print(f"Training set size: {train.count()}, Test set size: {test.count()}")

# Train model
print("Training model...")
model = pipeline.fit(train)
print("Model training completed!")

# Save model
print(f"Saving model to: {MODEL_PATH}")
model.write().overwrite().save(MODEL_PATH)
print("Model saved successfully!")

# Evaluate
preds = model.transform(test)
print("Model predictions:")
preds.select('Rent', 'prediction').show(5)

# Calculate basic metrics
from pyspark.ml.evaluation import RegressionEvaluator
evaluator = RegressionEvaluator(labelCol='Rent', predictionCol='prediction', metricName='rmse')
rmse = evaluator.evaluate(preds)
print(f"Root Mean Square Error: {rmse}")

evaluator.setMetricName('r2')
r2 = evaluator.evaluate(preds)
print(f"R-squared: {r2}")

spark.stop()
print("Spark job completed successfully!") 