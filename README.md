# Schema API 🕷️

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=flat&logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Schema API** is a powerful tool designed to extract, analyze, and audit structured data (Schema.org, JSON-LD, OpenGraph) from websites. It provides actionable insights to improve SEO, validates against Google's Rich Results requirements, and visualizes entity relationships.

## 🚀 Features

- **Deep Schema Extraction**: Extracts JSON-LD, Microdata, and OpenGraph data.
- **SEO Health Audit**: Analyzes structured data for errors, warnings, and missing recommended fields.
- **Rich Results Validation**: Checks eligibility for Google Rich Results (Product, Article, Recipe, Event, etc.).
- **Entity Graph**: Builds a graph of entities and their relationships (e.g., `isPartOf`, `author`, `publisher`).
- **Identity Resolution**: Automatically detects and consolidates Organization, WebSite, and WebPage identities.
- **Actionable Insights**: Returns prioritized actions (Critical, Recommended, Optional) to fix SEO issues.
- **Trust Signals**: Evaluates E-E-A-T signals like social profiles, contact info, and Wikidata links.

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Docker (optional, for containerized deployment)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd schema-api
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```
   The API will be available at `http://localhost:3015`.

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d --build
   ```

2. **Verify deployment**
   Check if the container is running:
   ```bash
   docker ps
   ```

## 📖 API Documentation

### 1. Analyze URL
Performs a deep analysis of the structured data on a given page.

- **Endpoint**: `/analyze`
- **Method**: `POST`
- **Content-Type**: `application/json`

**Request Body:**
```json
{
  "url": "https://example.com/article-page"
}
```

**Response Example:**
```json
{
  "url": "https://example.com/article-page",
  "summary": {
    "health": "needs_work",
    "critical_issues": 0,
    "recommended_actions": 2,
    "entities_found": 5
  },
  "actions": {
    "critical": [],
    "recommended": [
      {
        "action": "add_recommended_field",
        "target": "Article",
        "field": "dateModified",
        "reason": "Recommended for better Article display"
      }
    ]
  },
  "rich_results": {
    "eligible": ["Breadcrumb trail"],
    "potential": ["Article rich results"]
  }
}
```

### 2. Extract Raw Schema (Legacy)
Returns the raw extracted metadata without analysis.

- **Endpoint**: `/extract-schema`
- **Method**: `POST`

**Request Body:**
```json
{
  "url": "https://example.com"
}
```

### 3. Health Check
Checks if the API is running.

- **Endpoint**: `/health`
- **Method**: `GET`
- **Response**: `OK`

## 🐳 Deployment

This project is configured for deployment with **Coolify** and **Traefik**.
Check `docker-compose.yml` for configuration details.

- **Port**: `3015`
- **Network**: `coolify`
- **Traefik Labels**: Configured for `schema.strudel.marketing` (adjust as needed).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.
