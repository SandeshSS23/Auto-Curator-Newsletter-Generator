from typing import List
from newsapi import NewsApiClient
from dotenv import load_dotenv
import os
import requests

load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-8b-8192"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

newsapi = NewsApiClient(api_key=NEWSAPI_KEY)
class NewsletterAgent:
    def __init__(self, topics: List[str]):
        self.topics = topics
        self.articles_map = {}
        self.summaries_map = {}

    def fetch_articles(self):
        for topic in self.topics:
            articles = newsapi.get_everything(q=topic, language='en', page_size=5)
            self.articles_map[topic] = [(a['title'], a['url'], a['description']) for a in articles['articles']]

    def summarize_articles(self):
        for topic, articles in self.articles_map.items():
            prompt = f"Create a short, newsletter-style summary for these articles on {topic} with key highlights:\n\n"
            for title, url, desc in articles:
                prompt += f"Title: {title}\nDescription: {desc}\nLink: {url}\n\n"

            response = requests.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a helpful newsletter summarizer agent."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7
                }
            )

            if response.status_code == 200:
                self.summaries_map[topic] = response.json()["choices"][0]["message"]["content"]
            else:
                self.summaries_map[topic] = f"<p>Summary unavailable due to API error for {topic}.</p>"

    def compile_newsletter(self) -> str:
        newsletter_html = ""
        for topic in self.topics:
            newsletter_html += f"<h2>{topic}</h2><br>{self.summaries_map.get(topic, '')}<br><br>"
        return newsletter_html

