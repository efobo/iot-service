
import requests
import time
import random
import argparse
from threading import Thread

def generate_data(device_id, frequency, endpoint):
    """
    Генерирует данные для устройства и отправляет их на заданный эндпоинт.
    
    Args:
        device_id (int): Идентификатор устройства.
        frequency (float): Частота сообщений (в сообщениях в секунду).
        endpoint (str): URL эндпоинта IoT Controller.
    """
    interval = 1 / frequency
    while True:
        data = {
            "device_id": device_id,
            "field_a": random.randint(0, 10),  # Генерация случайного значения
        }
        try:
            response = requests.post(endpoint, json=data)
            if response.status_code == 200:
                print(f"[Device {device_id}] Data sent: {data}")
            else:
                print(f"[Device {device_id}] Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[Device {device_id}] Failed to send data: {e}")
        time.sleep(interval)

def main():
    """
    parser = argparse.ArgumentParser(description="Data Simulator for IoT devices.")
    parser.add_argument("--devices", type=int, default=10, help="Количество устройств")
    parser.add_argument("--frequency", type=float, default=1.0, help="Частота сообщений (в сообщениях в секунду)")
    parser.add_argument("--endpoint", type=str, required=True, help="URL эндпоинта IoT Controller")
    args = parser.parse_args()
    """
    threads = []
    for device_id in range(1, 100 + 1):
        thread = Thread(target=generate_data, args=(device_id, 1, "http://localhost:50051/data"))
        thread.daemon = True
        threads.append(thread)
        thread.start()
    
    # Ожидание завершения всех потоков
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("Data Simulator stopped.")

if __name__ == "__main__":
    main()



