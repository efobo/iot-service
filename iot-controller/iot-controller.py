# IoT Controller
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
import pika
import json
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (можно изменить на DEBUG для подробных логов)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Логи в консоль
    ]
)
logger = logging.getLogger("IoT Controller")

app = FastAPI()

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
async def receive_data(data: dict):
    try:
        # Логирование входящих данных
        logger.info(f"Received data: {data}")

        # Валидация данных
        if "device_id" not in data or "field_a" not in data:
            logger.warning("Invalid data format received.")
            raise HTTPException(status_code=400, detail="Invalid data format")

        # Сохранение в MongoDB
        collection.insert_one(data)
        logger.info(f"Data saved to MongoDB: {data}")

        # Публикация в RabbitMQ
        channel.basic_publish(exchange='', routing_key='iot_data', body=json.dumps(data))
        logger.info(f"Data published to RabbitMQ: {data}")

        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=50051)

