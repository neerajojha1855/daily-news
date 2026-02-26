# 📰 DailyNews

DailyNews is a modern, responsive full-stack Django web application that curates top headlines from across the web. It features a customizable user preference system for tailored news feeds and integrates Google's Gemini AI to automatically generate concise executive summaries for every article, ensuring readers get the core facts instantly.

## ✨ Features

- **Personalized News Feed:** Users can create an account and select their preferred categories (Technology, Business, Sports, Entertainment, Health, Science, Politics, World News) to customize their homepage.
- **AI-Powered Summaries:** Integrated with Google Gemini AI to generate "✨ AI Executive Summaries" for fetched articles automatically.
- **Categorized Browsing:** Filter news by dynamic categories using intuitive tag-based navigation.
- **Responsive Dark Theme:** A premium, modern UI built with custom CSS, featuring glassmorphism elements, subtle hover animations, and a cohesive dark aesthetic.
- **Background Fetching:** A custom Django management command (`fetch_news`) reliably ingests, deduplicates, and summarizes articles from the News API.
- **Article Bookmarking (Favorites):** Save articles to read later (Infrastructure in place).

## 🛠️ Technology Stack

- **Backend:** Python, Django 6.0
- **Database:** PostgreSQL (Configured) / SQLite (Development)
- **Frontend:** Vanilla HTML, CSS, JavaScript (Django Templates)
- **APIs:** NewsAPI (News Aggregation), Google Gemini API (AI Summarization)
- **Architecture:** Monolithic Django app designed with modular apps (`users`, `articles`, `categories`, `favorites`)

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- [NewsAPI Key](https://newsapi.org/)
- [Google Gemini API Key](https://aistudio.google.com/)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://www.github.com/neerajojha1855/daily-news/
   cd DailyNews
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Unix/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration:**
   Create a `.env` file in the root directory (alongside `manage.py`) and add your API keys and database configuration:
   ```env
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   NEWS_API_KEY=your_newsapi_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # Optional: PostgreSQL Database Config
   # DB_NAME=dailynews
   # DB_USER=postgres
   # DB_PASSWORD=your_password
   # DB_HOST=localhost
   # DB_PORT=5432
   ```

5. **Apply Migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Fetch Initial News Data:**
   Run the custom management command to pull articles from NewsAPI and generate AI summaries:
   ```bash
   python manage.py fetch_news
   ```

7. **Run the Development Server:**
   ```bash
   python manage.py runserver
   ```
   *The application will be available at `http://127.0.0.1:8000/`*

## 📁 Project Structure

- `config/` - Main Django configuration, routing, and settings.
- `articles/` - Core logic for fetching, storing, and displaying news articles. Includes the `fetch_news` management command.
- `users/` - Custom user model, authentication, and preference tracking.
- `categories/` - Models and logic for sorting news by topics.
- `favorites/` - Models handling user bookmarks.
- `templates/` - Global HTML layouts (`base.html`, `footer.html`) and application-specific views.
- `static/css/style.css` - Global dark theme stylesheet.

## 🔮 Future Enhancements
- Infinite scroll pagination for seamless browsing.
- Intelligent recommendation engine based on user reading habits.
- Dedicated user dashboard for managing saved "Favorite" articles.
- Migration of the `fetch_news` script to a periodic Celery background task.
# daily-news
