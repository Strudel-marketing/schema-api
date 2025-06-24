FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git curl && apt-get clean

COPY . .

RUN pip install --no-cache-dir flask extruct requests beautifulsoup4 lxml

CMD ["python", "app.py"]