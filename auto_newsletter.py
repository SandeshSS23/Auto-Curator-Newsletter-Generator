from agent import NewsletterAgent

# Example usage
agent = NewsletterAgent(["global warming", "AI", "India election"])
agent.fetch_articles()
agent.summarize_articles()
newsletter_html = agent.compile_newsletter()

# Save and send
from utils import save_newsletter, send_email
save_newsletter(newsletter_html)
send_email("Your AI-Powered Newsletter", "newsletter.html")
