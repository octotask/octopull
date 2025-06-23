FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY auto_fork_sync.py .

ENTRYPOINT ["python", "auto_fork_sync.py"]
