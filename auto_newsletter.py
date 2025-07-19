# auto_newsletter.py

from agent import NewsletterAgent
from utils import save_newsletter, send_email
from trends import fetch_trending_from_gnews

topics = fetch_trending_from_gnews()

if not topics:
    print("❌ No trending topics fetched.")
    exit()

agent = NewsletterAgent(topics)
agent.fetch_articles()
agent.summarize_articles()
newsletter_html = agent.compile_newsletter()

save_newsletter(newsletter_html)
send_email("🗞️ Your AI-Powered Newsletter", "newsletter.html")

print("✅ Newsletter sent successfully!")
