import streamlit as st
import requests
from newsapi import NewsApiClient
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List
import os

load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASS = os.getenv("SENDER_PASS")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-8b-8192"

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


def save_newsletter(content: str, filename="newsletter.html"):
    html_content = content.replace('\n', '<br>')
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"<html><body>{html_content}</body></html>")


def send_email(subject: str, html_path: str):
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    part = MIMEText(html_content, "html")
    msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASS)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())


st.set_page_config(page_title="AI Newsletter Generator", page_icon="📰")
st.title("🧠 AI-Powered Newsletter Generator")
st.markdown("Generate & Email trending topic summaries using GROQ agents.")

topic_input = st.text_input("Enter topics (comma-separated)", placeholder="e.g., AI, Startups, Design")


def fetch_trending_from_gnews():
    api_key = os.getenv("GNEWS_API_KEY")
    if not api_key:
        raise ValueError("❌ GNEWS_API_KEY not found in environment")

    url = f"https://gnews.io/api/v4/top-headlines?lang=en&country=in&max=5&apikey={api_key}"
    response = requests.get(url)

    try:
        data = response.json()
    except ValueError:
        print("❌ Failed to parse JSON response")
        return []

    if "articles" in data:
        topics = [article["title"] for article in data["articles"]]
        return topics
    else:
        print("❌ GNews error response:", data)
        return []
    
use_trending = st.checkbox("Use trending topics from GNews (India)", value=False)

if use_trending:
    topics = fetch_trending_from_gnews()
    if topics:
        st.write("🟢 Using trending topics:", topics)
    else:
        topics = []
        st.error("❗ Could not fetch trending topics. Please enter custom topics.")
else:
    topic_input = st.text_input("Enter topics (comma-separated):")
    topics = [topic.strip() for topic in topic_input.split(",") if topic.strip()]
    if topics:
        st.write("🟢 Using custom topics:", topics)

if st.button("Generate & Send Newsletter"):
    if not topics:
        st.error("❗ Please enter at least one topic or enable 'Use trending topics'.")
    else:
        st.info("📥 Fetching articles, generating summaries, and sending email...")

        agent = NewsletterAgent(topics)
        agent.fetch_articles()
        agent.summarize_articles()
        newsletter_html = agent.compile_newsletter()

        save_newsletter(newsletter_html)
        send_email("Your AI-Powered Newsletter", "newsletter.html")

        st.success("✅ Newsletter sent successfully!")