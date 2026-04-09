import requests
from bs4 import BeautifulSoup
import random

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
    # add more
]

def get_auction_info(vin: str) -> dict:
    """Try Copart first, then IAAI. Fallback to empty data."""
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    result = {"copart": None, "iaai": None}
    # Copart
    try:
        url = f"https://www.copart.com/lotSearchResults?free=true&query={vin}"
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Scrape basic info (example)
        lot = soup.find('a', {'class': 'lotNumber'})
        if lot:
            result["copart"] = {
                "lot": lot.text.strip(),
                "status": "Available"  # you can parse more
            }
    except Exception:
        pass
    # IAAI
    try:
        url = f"https://www.iaai.com/Search?url=si&searchText={vin}"
        resp = requests.get(url, headers=headers, timeout=10)
        # parsing logic
        result["iaai"] = {"available": True}
    except:
        pass
    return result