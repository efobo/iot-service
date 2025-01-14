from fastapi import FastAPI, HTTPException, Request
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
from pymongo import MongoClient
import pika
import json
import logging
import logstash
import time
from fastapi.responses import PlainTextResponse

# Настройка логирования
LOGSTASH_HOST = 'logstash'
LOGSTASH_PORT = 5228

logger = logging.getLogger('python-logstash-logger')
logstash_handler = logstash.TCPLogstashHandler(LOGSTASH_HOST, LOGSTASH_PORT, version=1)
logger.addHandler(logstash_handler)

app = FastAPI()

# Метрики Prometheus
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "http_status"]
)
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "Histogram of request processing duration",
    ["method", "endpoint"]
)
MONGODB_OPERATIONS = Counter(
    "mongodb_operations_total",
    "Total number of MongoDB operations",
    ["operation", "status"]
)
RABBITMQ_OPERATIONS = Counter(
    "rabbitmq_operations_total",
    "Total number of RabbitMQ operations",
    ["operation", "status"]
)

# Подключение к MongoDB
try:
    mongo_client = MongoClient("mongodb://mongo:27017")
    db = mongo_client["iot"]
    collection = db["messages"]
    logger.info("Connected to MongoDB successfully.")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise

# Подключение к RabbitMQ
try:
    rabbitmq_connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = rabbitmq_connection.channel()
    channel.queue_declare(queue='iot_data')
    logger.info("Connected to RabbitMQ successfully.")
except Exception as e:
    logger.error(f"Failed to connect to RabbitMQ: {e}")
    raise

@app.post("/data")
async def receive_data(data: dict, request: Request):
    start_time = time.time()
    try:
        # Логирование входящих данных
        logger.info(f"Received data: {data}")

        # Валидация данных
        if "device_id" not in data or "field_a" not in data:
            logger.warning("Invalid data format received.")
            REQUEST_COUNT.labels(method=request.method, endpoint="/data", http_status=400).inc()
            raise HTTPException(status_code=400, detail="Invalid data format")

        # Сохранение в MongoDB
        try:
            collection.insert_one(data)
            logger.info(f"Data saved to MongoDB: {data}")
            MONGODB_OPERATIONS.labels(operation="insert", status="success").inc()
        except Exception as e:
            MONGODB_OPERATIONS.labels(operation="insert", status="error").inc()
            raise e

        # Публикация в RabbitMQ
        try:
            data['_id'] = str(data['_id'])
            channel.basic_publish(exchange='', routing_key='iot_data', body=json.dumps(data))
            logger.info(f"Data published to RabbitMQ: {data}")
            RABBITMQ_OPERATIONS.labels(operation="publish", status="success").inc()
        except Exception as e:
            RABBITMQ_OPERATIONS.labels(operation="publish", status="error").inc()
            raise e

        REQUEST_COUNT.labels(method=request.method, endpoint="/data", http_status=200).inc()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        REQUEST_COUNT.labels(method=request.method, endpoint="/data", http_status=500).inc()
        return {"status": "error", "message": str(e)}
    finally:
        duration = time.time() - start_time
        REQUEST_DURATION.labels(method=request.method, endpoint="/data").observe(duration)

@app.get("/metrics")
async def metrics():
    # Возвращаем текущие метрики в формате Prometheus
    return PlainTextResponse(generate_latest(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=50051)



