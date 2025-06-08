
# 📦 schema-api

A FastAPI-based service for crawling pages, analyzing structure, generating structured data (JSON-LD), and organizing URLs by logic or cluster.

---

## 🚀 API Endpoints

### 🗺️ `POST /sitemap`

**Description:**  
Extracts up to 100 URLs from a sitemap using `advertools`.

**Request Body:**
```json
{
  "url": "https://example.com/sitemap.xml"
}
```

| Field | Type   | Required | Description                |
|-------|--------|----------|----------------------------|
| url   | string | ✅       | URL of the sitemap to read |

**Response Example:**
```json
{
  "urls": [
    "https://example.com/page1",
    "https://example.com/page2"
  ]
}
```

---

### 🧠 `POST /schema`

**Description:**  
Fetches a page, extracts metadata and existing JSON-LD schemas, and returns a generated schema suggestion.

**Request Body:**
```json
{
  "url": "https://example.com"
}
```

| Field | Type   | Required | Description       |
|-------|--------|----------|-------------------|
| url   | string | ✅       | URL of the webpage |

**Response Example:**
```json
{
  "from_existing_schema": ["WebPage"],
  "used_type": "WebPage",
  "schema": {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "url": "https://example.com",
    "name": "Example Title",
    "description": "Example description"
  },
  "extract": {
    "word_count": 150,
    "n_tokens": 170,
    "avg_token_length": 4.5
  }
}
```

---

### ✂️ `POST /extract`

**Description:**  
Extracts NLP features from raw text using `advertools`.

**Request Body:**
```json
{
  "text": "This is some text to analyze."
}
```

| Field | Type   | Required | Description        |
|-------|--------|----------|--------------------|
| text  | string | ✅       | Raw text to analyze |

**Response Example:**
```json
{
  "word_count": 7,
  "n_tokens": 8,
  "avg_token_length": 4.0
}
```

---

### 🧪 `POST /validate-entity`

**Description:**  
Stub endpoint for future validation logic. Returns the input for now.

**Request Body:**
```json
{
  "type": "Organization",
  "properties": {
    "name": "Strudel Marketing"
  }
}
```

**Response Example:**
```json
{
  "message": "Validation logic coming soon",
  "received": {
    "type": "Organization",
    "properties": {
      "name": "Strudel Marketing"
    }
  }
}
```

---

### 🧭 `POST /cluster`

**Description:**  
Clusters URLs from a sitemap by directory level using `advertools`.

**Request Body:**
```json
{
  "url": "https://example.com/sitemap.xml",
  "level": 2
}
```

| Field  | Type   | Required | Description                        |
|--------|--------|----------|------------------------------------|
| url    | string | ✅       | URL of the sitemap                 |
| level  | int    | ✅       | Directory level (e.g., 1, 2, 3...) |

**Response Example:**
```json
{
  "cluster_by": "dir_2",
  "clusters": {
    "blog": 18,
    "products": 5
  }
}
```

---

### 📄 `GET /existing-schema`

**Description:**  
Extracts all JSON-LD structured data (`<script type="application/ld+json">`) from a webpage.

**Query Parameter:**
```
?url=https://example.com
```

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

### ❤️ `GET /`

**Description:**  
Health check endpoint.

**Response Example:**
```json
{
  "status": "running"
}
```
