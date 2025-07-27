FROM bitnami/spark:3.4.1
USER root
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
USER 1001
COPY preprocess_and_train.py ./
CMD ["/opt/bitnami/spark/bin/spark-submit", "/app/preprocess_and_train.py"] 