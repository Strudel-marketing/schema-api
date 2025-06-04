from flask import Flask, request, jsonify
import advertools as adv
import pandas as pd
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# 🔹 1. sitemap endpoint
@app.route("/sitemap", methods=["POST"])
def process_sitemap():
    data = request.get_json()
    sitemap_url = data.get("url")
    if not sitemap_url:
        return jsonify({"error": "Missing 'url'"}), 400

    try:
        df = adv.sitemap_to_df(sitemap_url)
        urls = df["loc"].dropna().tolist()
        return jsonify({"urls": urls[:100]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 2. schema creation from URL
@app.route("/schema", methods=["POST"])
def generate_schema():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing 'url'"}), 400

    try:
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        extract = adv.extract_text([text]).to_dict()

        title = soup.title.string if soup.title else ""
        description = soup.find("meta", attrs={"name": "description"}).get("content", "") if soup.find("meta", attrs={"name": "description"}) else ""

        # 🔍 Try to find existing schema type
        existing_types = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                parsed = script.string
                if not parsed:
                    continue
                data = json.loads(parsed)
                if isinstance(data, list):
                    existing_types.extend([item.get("@type") for item in data if "@type" in item])
                elif "@type" in data:
                    existing_types.append(data["@type"])
            except Exception:
                continue

        main_type = existing_types[0] if existing_types else "WebPage"

        schema = {
            "@context": "https://schema.org",
            "@type": main_type,
            "url": url,
            "name": title,
            "description": description
        }

        return jsonify({
            "from_existing_schema": existing_types,
            "used_type": main_type,
            "schema": schema,
            "extract": extract
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 3. basic extract from text
@app.route("/extract", methods=["POST"])
def extract_text():
    data = request.get_json()
    text = data.get("text", "")
    try:
        extract = adv.extract.extract_text([text])
        return jsonify(extract.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 4. placeholder for entity validation
@app.route("/validate-entity", methods=["POST"])
def validate_entity():
    data = request.get_json()
    return jsonify({"message": "Validation logic coming soon", "received": data})

# 🔹 5. clustering by URL structure
@app.route("/cluster", methods=["POST"])
def cluster_urls():
    data = request.get_json()
    sitemap_url = data.get("url")
    level = data.get("level", 1)

    if not sitemap_url:
        return jsonify({"error": "Missing 'url'"}), 400

    try:
        sitemap_df = adv.sitemap_to_df(sitemap_url)
        urls = sitemap_df["loc"].dropna().tolist()

        url_df = adv.url_to_df(urls)
        dir_col = f"dir_{level}"
        if dir_col not in url_df.columns:
            return jsonify({"error": f"Invalid level: {level}. Available: dir_1 to dir_{len(url_df.columns)-1}"}), 400

        grouped = url_df[dir_col].value_counts().to_dict()

        return jsonify({
            "cluster_by": dir_col,
            "clusters": grouped
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
