import requests
import os

def fetch_trending_from_gnews():
    GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
    url = f"https://gnews.io/api/v4/top-headlines?lang=en&country=us&max=5&apikey={GNEWS_API_KEY}"

    response = requests.get(url)
    data = response.json()

    if "errors" in data:
        print(f"❌ GNews error response: {data}")
        return []

    topics = [article["title"] for article in data["articles"]]
    return topics
