from flask import Flask, request, jsonify
import advertools as adv

app = Flask(__name__)

@app.route("/sitemap", methods=["POST"])
def process_sitemap():
    data = request.get_json()
    sitemap_url = data.get("url")

    if not sitemap_url:
        return jsonify({"error": "Missing 'url'"}), 400

    try:
        df = adv.sitemap_to_df(sitemap_url)
        urls = df["loc"].dropna().tolist()
        return jsonify({"urls": urls[:100]})  # מגביל ל-100 שורות לדוגמה
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
