from flask import Flask, request, jsonify
from schema_scraper import scrape
import traceback

app = Flask(__name__)

@app.route("/extract-schema", methods=["POST"])
def extract_schema():
    try:
        data = request.get_json()
        url = data.get("url")
        if not url:
            return jsonify({"error": "Missing 'url' parameter"}), 400

        result = scrape(url)
        return jsonify({"schemas": result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})