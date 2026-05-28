# serpapi_client.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()
SERP_API_KEY = os.getenv("SERP_API_KEY")

def fetch_laptop_prices(query: str, max_results: int = 20):
    """
    SerpApi se data fetch karta hai aur clean list return karta hai.
    Ab ye zyada results fetch karega taaki filtering ke baad bhi options bachein.
    """
    if not SERP_API_KEY:
        print("Error: SERP_API_KEY not found in .env file.")
        return []

    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": SERP_API_KEY,
        "gl": "in", # India results
        "hl": "en", # English language
        "num": max_results
    }

    try:
        response = requests.get("https://serpapi.com/search.json", params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"SerpApi Connection Error: {e}")
        return []

    results = []
    shopping_results = data.get("shopping_results", [])

    if not shopping_results:
        print("No shopping results found for this query.")
        return []

    for item in shopping_results:
        # 1. Price Cleaning Logic
        price_raw = item.get("price", "0")
        price_val = 0
        
        if price_raw:
            try:
                # Remove currency symbols, commas, and handle decimal parts
                clean_str = str(price_raw).replace("₹", "").replace(",", "").replace("Rs.", "").strip()
                # Split at space for cases like "₹ 50,000 onwards"
                clean_str = clean_str.split()[0]
                price_val = int(float(clean_str))
            except (ValueError, IndexError):
                price_val = 0

        # 2. Source/Platform
        source = item.get("source", "Online Store")
        
        # 3. Specs/Snippet
        # SerpApi 'snippet' ya 'extensions' mein specs deta hai
        extensions = item.get("extensions", [])
        specs_text = " • ".join(extensions) if extensions else item.get("snippet", "")

        results.append({
            "platform": source,
            "title": item.get("title", "Laptop"),
            "price_value": price_val,
            "price_str": f"₹{price_val:,}", 
            "image": item.get("thumbnail", ""),
            "link": item.get("link") or item.get("product_link", ""),
            "ram_type" :item.get("ram_type", ""),
            "ram":item.get("ram", ""),
            "storage_type": item.get("storage_type", ""),
            "storage": item.get("storage", ""),
            "specs": specs_text
        })

    return results

