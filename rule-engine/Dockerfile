FROM python:3.9-slim

WORKDIR /app

COPY rule-engine.py ./
COPY requirements.txt ./
COPY .env ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "rule-engine.py"]

