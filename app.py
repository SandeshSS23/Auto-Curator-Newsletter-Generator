import streamlit as st
import requests
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List
import os
from agent import NewsletterAgent

load_dotenv()


GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASS = os.getenv("SENDER_PASS")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")


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