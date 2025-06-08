# 📦 schema-api

A lightweight FastAPI-based service for crawling pages, generating structured data schemas (JSON-LD), and extracting existing schemas from websites.

---

## 🚀 Endpoints

### 🔍 `POST /generate`

**Description:**  
Crawls a website using `advertools` and returns page-level data (title, headings, meta tags, links, etc.).

**Request Body:**
```json
{
  "url": "https://example.com",
  "level": 1
}
```

| Field   | Type     | Required | Description                     |
|---------|----------|----------|---------------------------------|
| `url`   | `string` | ✅       | The page URL to crawl           |
| `level` | `integer`| ❌       | Crawl depth (default = 1)       |

**Response Example:**
```json
{
  "url": ["https://example.com"],
  "title": ["Welcome to Example"],
  "meta_description": ["This is a demo page."]
}
```

---

### 🧠 `POST /schema`

**Description:**  
Generates a valid [schema.org](https://schema.org) JSON-LD structured data markup from a text input using the `llama3` model via [Ollama](https://ollama.com/).

**Request Body:**
```json
{
  "text": "Strudel Marketing is a boutique SEO agency based in Tel Aviv.",
  "url": "https://strudel.marketing"
}
```

| Field   | Type     | Required | Description                                      |
|---------|----------|----------|--------------------------------------------------|
| `text`  | `string` | ✅       | Descriptive content to base the schema on       |
| `url`   | `string` | ❌       | Optional URL to include in the schema           |

**Response Example:**
```json
{
  "schema": {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Strudel Marketing",
    "url": "https://strudel.marketing",
    "description": "A boutique SEO agency based in Tel Aviv."
  }
}
```

---

### 📄 `GET /existing-schema`

**Description:**  
Extracts any existing JSON-LD structured data from a web page.

**Query Parameters:**
```
?url=https://example.com
```

| Parameter | Type     | Required | Description             |
|-----------|----------|----------|-------------------------|
| `url`     | `string` | ✅       | URL of the page to scan |

**Response Example:**
```json
{
  "schemas": [
    {
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "Example Article"
    }
  ]
}
```

---

## ⚙️ Configuration

- `/schema` is powered by your self-hosted Ollama instance at:

```
https://ollama.strudel.marketing
```

Ensure that the model is available:

```bash
ollama pull llama3
```

---

## 🛠 Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [advertools](https://github.com/eliasdabbas/advertools)
- [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)
- [Ollama](https://ollama.com) (for local LLM inference)

---

## 📄 License

MIT © Strudel Marketing
