import requests
from bs4 import BeautifulSoup

def fetch_url_text(url: str) -> str:
    if not url.startswith("http"):
        return f"Invalid URL: {url}"
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        # Remove noisy elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
            
        text = soup.get_text(separator="\n", strip=True)
        # Prevent massive token consumption
        return text[:10000]
    except Exception as e:
        return f"Error fetching URL content: {str(e)}"
