import pika
from pymongo import MongoClient
import json
from collections import defaultdict
import logging
import logstash
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE")
LOGSTASH_HOST = os.getenv("LOGSTASH_HOST")
LOGSTASH_PORT = int(os.getenv("LOGSTASH_PORT"))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)


logger = logging.getLogger("Rule Engine")

logstash_handler = logstash.TCPLogstashHandler(LOGSTASH_HOST, LOGSTASH_PORT, version=1)
logger.addHandler(logstash_handler)
# Подключение к MongoDB
try:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    logger.info("Connected to MongoDB successfully.")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise

# Подключение к RabbitMQ
try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE)
    logger.info("Connected to RabbitMQ successfully.")
except Exception as e:
    logger.error(f"Failed to connect to RabbitMQ: {e}")
    raise

# Хеш-таблица для хранения состояния устройств
device_state = defaultdict(list)

def process_instant_rule(data):
    """
    Мгновенное правило: Значение поля А от устройства 42 больше 5.
    """
    try:
        if data.get("device_id") == 42 and data.get("field_a", 0) > 5:
            alert = {
                "device_id": data["device_id"],
                "rule": "field_a > 5",
                "timestamp": data.get("timestamp")
            }
            collection.insert_one(alert)
            logger.info(f"Instant rule triggered: {alert}")
    except Exception as e:
        logger.error(f"Error processing instant rule: {e}")

def process_continuous_rule(data):
    """
    Длящееся правило: Значение поля А от устройства 42 больше 5 на протяжении 10 пакетов.
    """
    try:
        device_id = data.get("device_id")
        if device_id == 42:
            device_state[device_id].append(data)
            if len(device_state[device_id]) > 10:
                device_state[device_id].pop(0)

            if all(packet["field_a"] > 5 for packet in device_state[device_id]):
                alert = {
                    "device_id": device_id,
                    "rule": "field_a > 5 for 10 messages",
                    "timestamp": data.get("timestamp")
                }
                collection.insert_one(alert)
                logger.info(f"Continuous rule triggered: {alert}")
    except Exception as e:
        logger.error(f"Error processing continuous rule: {e}")

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        logger.info(f"Received message: {data}")
        process_instant_rule(data)
        process_continuous_rule(data)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode message: {e}")
    except Exception as e:
        logger.error(f"Error in callback: {e}")

channel.basic_consume(queue='iot_data', on_message_callback=callback, auto_ack=True)

logger.info("Rule Engine is running...")
try:
    channel.start_consuming()
except KeyboardInterrupt:
    logger.info("Rule Engine stopped.")
except Exception as e:
    logger.error(f"Error in main loop: {e}")

