FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pin_bruteforce.py .

VOLUME ["/app/data"]

CMD ["python", "pin_bruteforce.py"]
