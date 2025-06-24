FROM python:3.11-slim

WORKDIR /app

COPY . .

# הוספת git לפני התקנת requirements
RUN apt-get update && apt-get install -y git && \
    pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
