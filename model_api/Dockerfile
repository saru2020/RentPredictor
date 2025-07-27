FROM bitnami/spark:3.4.1

USER root
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3
ENV SPARK_LOCAL_IP=127.0.0.1
ENV SPARK_LOCAL_DIRS=/tmp
ENV JAVA_OPTS="-Xmx2g -Xms1g"

# Switch back to spark user
USER 1001

CMD ["python", "app.py"] 