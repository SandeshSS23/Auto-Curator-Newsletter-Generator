# 📰 Auto-Curator Newsletter Generator

**Auto-Curator Newsletter Generator** is a fully automated Python-based application that uses generative AI to create and deliver personalized newsletters. It combines the power of large language models (LLMs), the NewsAPI, and Streamlit to make your daily news summary effortless.

## ✨ Features

- 🔍 Fetches the latest news articles for any given topic using NewsAPI
- 🧠 Summarizes news content using LLMs like **Groq**
- 🖥️ Generates a clean, readable HTML newsletter
- 📩 Sends the newsletter directly to your email inbox via SMTP
- ⚙️ Automates the entire process using **GitHub Actions Cron Jobs**

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/auto-curator-newsletter.git
cd auto-curator-newsletter
```

2. Install Dependencies
Create a virtual environment and install the required packages:

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

pip install -r requirements.txt
```

3. Setup Environment Variables
Create a .env file in the root directory with the following contents:

.env
```
NEWS_API_KEY=your_newsapi_key
GROQ_API_KEY=your_groq_key
SENDER_EMAIL=your_email@gmail.com
SENDER_PASS=your_app_password     # Use Gmail App Passwords for secure login
RECEIVER_EMAIL=recipient@example.com
```

🖥️ Run the App Locally
```bash
streamlit run Frontend.py
```

🛠️ Tech Stack
Python 3.11+
Streamlit for the web interface
Groq for summarization
NewsAPI for fetching news
SMTP for sending emails
GitHub Actions for automation


🧑‍💻 Author
Made with ❤️ by Your Sandesh

