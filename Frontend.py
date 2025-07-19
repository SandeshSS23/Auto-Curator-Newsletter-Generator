import streamlit as st
import requests
from newsapi import NewsApiClient
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


import os

load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASS = os.getenv("SENDER_PASS")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

newsapi = NewsApiClient(api_key=NEWSAPI_KEY)
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-8b-8192"  

def fetch_headlines(topic):
    articles = newsapi.get_everything(q=topic, language='en', page_size=5)
    return [(a['title'], a['url'], a['description']) for a in articles['articles']]

def summarize_news(topic, articles):
    prompt = f"Create a short, newsletter-style summary for these articles on {topic}:\n\n"
    for title, url, desc in articles:
        prompt += f"Title: {title}\nDescription: {desc}\nLink: {url}\n\n"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful newsletter summarizer."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=body)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print("Groq API error:", response.status_code, response.text)
        return "<p>Summary unavailable due to API error.</p>"
    

def save_newsletter(content, filename="newsletter.html"):
    html_content = content.replace('\n', '<br>')
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"<html><body>{html_content}</body></html>")

def send_email(subject, html_path):
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

st.title("📰 AI Newsletter Generator")

topic_input = st.text_input(
    "Enter topics (comma-separated)", 
    placeholder="e.g., AI, Startups, Design"
)

if st.button("Generate & Send Newsletter"):
    topics = [topic.strip() for topic in topic_input.split(",") if topic.strip()]
    if not topics:
        st.error("Please enter at least one topic.")
    else:
        st.info("Fetching articles and generating newsletter...")

        full_newsletter = ""
        for topic in topics:
            articles = fetch_headlines(topic)
            summary = summarize_news(topic, articles)
            full_newsletter += f"<h2>{topic}</h2>\n{summary}<br><br>"

        save_newsletter(full_newsletter)
        send_email("Your AI-Powered Newsletter", "newsletter.html")

        st.success("✅ Newsletter sent successfully!")
