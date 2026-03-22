FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git curl && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt beautifulsoup4 lxml

# Install Playwright Chromium browser for JS rendering (optional feature)
RUN playwright install chromium && playwright install-deps chromium

COPY . .

CMD ["python", "app.py"]