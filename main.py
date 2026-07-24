import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AuditRequest(BaseModel):
    url: str

@app.post("/api/audit")
def audit_url(data: AuditRequest):
    url = data.url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    start_time = time.time()
    try:
        # Fetch the URL with a 5-second timeout
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        response_time_ms = round((time.time() - start_time) * 1000, 2)
        
        # Check if content is HTML
        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            raise HTTPException(status_code=400, detail="Requested URL does not return HTML content.")

        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract metadata
        title = soup.title.string.strip() if soup.title and soup.title.string else "No Title Found"
        
        meta_desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        meta_desc = meta_desc_tag["content"].strip() if meta_desc_tag and meta_desc_tag.get("content") else "No Meta Description Found"
        
        h1_count = len(soup.find_all("h1"))
        
        # Count images missing alt attributes
        images = soup.find_all("img")
        missing_alt = sum(1 for img in images if not img.get("alt"))
        
        # Word count approximation
        text_content = soup.get_text()
        word_count = len(text_content.split())

        return {
            "status_code": response.status_code,
            "response_time_ms": response_time_ms,
            "title": title,
            "meta_description": meta_desc,
            "h1_count": h1_count,
            "missing_alt_images": missing_alt,
            "word_count": word_count
        }

    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Target website timed out.")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")