from flask import Flask, request, jsonify
import requests
import extruct
from bs4 import BeautifulSoup
from w3lib.html import get_base_url

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return 'OK', 200

@app.route('/extract-schema', methods=['POST'])
def extract_schema():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        html = requests.get(url, headers=headers, timeout=10).text
        base_url = get_base_url(html, url)
        metadata = extruct.extract(html, base_url=base_url)
        return jsonify(metadata)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3015)