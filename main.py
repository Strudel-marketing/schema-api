from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import advertools as adv
import requests
from bs4 import BeautifulSoup
import json

app = FastAPI()

class URLRequest(BaseModel):
    url: str
    level: int | None = 1

class TextRequest(BaseModel):
    text: str

@app.post("/sitemap")
async def process_sitemap(payload: URLRequest):
    try:
        df = adv.sitemap_to_df(payload.url)
        urls = df["loc"].dropna().tolist()
        return {"urls": urls[:100]}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/schema")
async def generate_schema(payload: URLRequest):
    try:
        html = requests.get(payload.url).text
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        try:
        extract = adv.extract.extract_text([text]).to_dict() 
except AttributeError:
    extract = {"text": text[:500] + "..." if len(text) > 500 else text}

        title = soup.title.string if soup.title else ""
        description = soup.find("meta", attrs={"name": "description"}).get("content", "") if soup.find("meta", attrs={"name": "description"}) else ""

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
            "url": payload.url,
            "name": title,
            "description": description
        }

        return {
            "from_existing_schema": existing_types,
            "used_type": main_type,
            "schema": schema,
            "extract": extract
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/extract")
async def extract_text(payload: TextRequest):
    try:
        extract = adv.extract.extract_text([payload.text])
        return extract.to_dict()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/validate-entity")
async def validate_entity(request: Request):
    data = await request.json()
    return {"message": "Validation logic coming soon", "received": data}

@app.post("/cluster")
async def cluster_urls(payload: URLRequest):
    try:
        sitemap_df = adv.sitemap_to_df(payload.url)
        urls = sitemap_df["loc"].dropna().tolist()
        url_df = adv.url_to_df(urls)
        dir_col = f"dir_{payload.level}"
        if dir_col not in url_df.columns:
            return JSONResponse(status_code=400, content={
                "error": f"Invalid level: {payload.level}. Available: dir_1 to dir_{len(url_df.columns)-1}"
            })

        grouped = url_df[dir_col].value_counts().to_dict()
        return {
            "cluster_by": dir_col,
            "clusters": grouped
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
async def health():
    return {"status": "running"}

@app.post("/existing-schema")
async def extract_existing_schema(payload: URLRequest):
    try:
        response = requests.get(payload.url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

    soup = BeautifulSoup(response.text, "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")

    schemas = []
    for script in scripts:
        try:
            data = json.loads(script.string)
            schemas.append(data)
        except:
            continue

    return {"schemas": schemas}

