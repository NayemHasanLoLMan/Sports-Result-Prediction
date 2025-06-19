import os
import requests
from dotenv import load_dotenv
from typing import Dict, Optional

load_dotenv()

STATPAL_API_KEY = os.environ.get('STATPAL_API_KEY')
if not STATPAL_API_KEY:
    raise ValueError("STATPAL_API_KEY not found in environment variables")

# Base URL and sports endpoints
BASE_URL = 'https://statpal.io/api/v1'
SPORTS = ['soccer', 'nhl', 'nba', 'nfl', 'mlb', 'tennis']

def fetch_sports_data() -> Optional[Dict[str, Dict]]:
    """Fetch live scores from sports APIs.

    Returns:
        A dictionary with sports as keys and API responses as values, or None if all requests fail.
    """
    sports_data = {}
    params = {"access_key": STATPAL_API_KEY}

    for sport in SPORTS:
        url = f"{BASE_URL}/{sport}/livescores"
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # Raise for bad status codes (e.g., 4xx, 5xx)
            sports_data[sport] = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch {sport} data: {e}")
            continue

    return sports_data if sports_data else None

if __name__ == "__main__":
    data = fetch_sports_data()
    if data:
        for sport, scores in data.items():
            print(f"{sport.upper()} Live Scores: {scores}")
    else:
        print("No sports data retrieved.")