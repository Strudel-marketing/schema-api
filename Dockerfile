FROM python:3.11-slim

WORKDIR /app

COPY . .

# 👇 כאן מתקינים את git לפני הרצת pip
RUN apt-get update && apt-get install -y git && \
    pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
