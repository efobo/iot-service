import time
import random
import json
import logging
import pika
import argparse

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования: INFO, DEBUG, ERROR
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Логи в консоль
    ]
)
logger = logging.getLogger("Data Simulator")

def generate_data(device_id):
    """
    Генерация случайных данных для устройства.
    """
    data = {
        "device_id": device_id,
        "field_a": random.randint(0, 10),
        "timestamp": time.time()
    }
    logger.debug(f"Generated data for device {device_id}: {data}")
    return data

def send_data_to_rabbitmq(message, channel):
    """
    Отправка данных в очередь RabbitMQ.
    """
    try:
        channel.basic_publish(exchange='', routing_key='iot_data', body=json.dumps(message))
        logger.info(f"Sent message to RabbitMQ: {message}")
    except Exception as e:
        logger.error(f"Failed to send message to RabbitMQ: {e}")

def main(device_count, message_rate):
    """
    Основная функция симуляции данных.
    """
    logger.info(f"Starting Data Simulator with {device_count} devices, {message_rate} messages per second.")
    
    # Подключение к RabbitMQ
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='iot_data')
        logger.info("Connected to RabbitMQ.")
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        return

    devices = list(range(1, device_count + 1))
    interval = 1 / message_rate

    try:
        while True:
            for device_id in devices:
                message = generate_data(device_id)
                send_data_to_rabbitmq(message, channel)
                time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Data Simulator stopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        connection.close()
        logger.info("Connection to RabbitMQ closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data Simulator for IoT system.")
    parser.add_argument(
        "--devices", type=int, required=True, help="Number of devices to simulate."
    )
    parser.add_argument(
        "--rate", type=float, required=True, help="Messages per second per device."
    )
    args = parser.parse_args()
    
    main(args.devices, args.rate)

