FROM python:3.9-slim

WORKDIR /app

COPY iot-controller.py ./
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "iot-controller.py"]

