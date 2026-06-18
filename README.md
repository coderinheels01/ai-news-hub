# AI News Hub

A personalized daily AI news digest pipeline that scrapes content from multiple sources, summarizes it using LLMs, ranks it based on a user profile, and delivers it as a formatted email — automatically, every day.

---

## Architecture Overview

```mermaid
flowchart TD
    subgraph Sources
        YT[YouTube RSS Feeds]
        OA[OpenAI Blog RSS]
        AN[Anthropic Blog RSS]
    end

    subgraph Scraping
        YTS[YouTube Scraper]
        ARS[Article Scraper]
    end

    subgraph Processing
        TR[Transcript Fetcher]
        DA[Digest Agent\ngpt-4o-mini]
    end

    subgraph DB[(PostgreSQL)]
        VT[youtube_videos]
        AR[article]
        DG[digest]
    end

    subgraph Delivery
        CA[Curator Agent\ngpt-4.1]
        EA[Email Agent\ngpt-4o-mini]
        GM[Gmail]
    end

    YT --> YTS
    OA --> ARS
    AN --> ARS

    YTS --> VT
    ARS --> AR

    VT --> TR --> VT
    VT --> DA
    AR --> DA
    DA --> DG

    DG --> CA
    CA --> EA
    EA --> GM
```

---

## Pipeline Steps

The pipeline runs daily via a Render cron job (`main.py` -> `app/daily_runner.py`):

### 1. Scraping (`app/runner.py`)
Fetches raw content from three sources:
- **YouTube** - RSS feed per channel, extracts video metadata. Transcripts are fetched separately via `youtube-transcript-api`.
- **OpenAI blog** - RSS feed (`openai.com/news/rss.xml`)
- **Anthropic blog** - Three RSS feeds (news, research, engineering) via a community-maintained mirror

Raw content is inserted into PostgreSQL, with `ON CONFLICT DO NOTHING` so re-runs are safe.

### 2. YouTube transcript processing (`app/services/process_youtube.py`)
Fetches transcripts for any YouTube videos that don't have one yet. Videos with no transcript available are marked `__UNAVAILABLE__` so they aren't retried.

### 3. Digest generation (`app/services/process_digest.py`)
For each undigested article or video, the `DigestAgent` (`gpt-4o-mini`) generates:
- A concise title
- A 2-3 sentence summary

Digests are stored in the `digest` table with a composite ID (`article_type:article_id`).

### 4. Curation (`app/agent/curator_agent.py`)
The `CuratorAgent` (`gpt-4.1`) ranks all recent digests against the user profile (defined in `app/profiles/user_profiles.py`). It scores each article 0-10 for relevance and returns a ranked list.

### 5. Email generation & delivery (`app/services/process_email.py`)
The `EmailAgent` (`gpt-4o-mini`) writes a personalized greeting and introduction for the top N articles. The final email is rendered as HTML and sent via Gmail SMTP.

---

## Project Structure

```
ai-news-hub/
├── main.py                          # Entry point for Render cron job
├── config.py                        # YouTube channel IDs
├── render.yaml                      # Render deployment config (cron + DB)
├── Dockerfile                       # Docker image definition
├── docker/docker-compose.yml        # Local PostgreSQL setup
│
├── app/
│   ├── daily_runner.py              # Orchestrates the full pipeline
│   ├── runner.py                    # Runs all scrapers
│   ├── logging_config.py            # Centralised logging setup
│   │
│   ├── scrapers/
│   │   ├── article.py               # Base RSS scraper
│   │   ├── anthropic_scraper.py     # Anthropic RSS feeds
│   │   ├── openai_scraper.py        # OpenAI RSS feed
│   │   └── youtube_scraper.py       # YouTube RSS + transcript fetcher
│   │
│   ├── agent/
│   │   ├── digest_agent.py          # Summarises articles (gpt-4o-mini)
│   │   ├── curator_agent.py         # Ranks digests by user profile (gpt-4.1)
│   │   └── email_agent.py           # Writes email intro (gpt-4o-mini)
│   │
│   ├── services/
│   │   ├── process_articles.py      # Converts articles to markdown
│   │   ├── process_youtube.py       # Fetches & stores transcripts
│   │   ├── process_digest.py        # Runs digest agent over undigested content
│   │   ├── process_curator.py       # Runs curation standalone
│   │   ├── process_email.py         # Generates and sends email digest
│   │   └── email.py                 # Gmail SMTP + HTML rendering
│   │
│   ├── database/
│   │   ├── connection.py            # SQLAlchemy engine + session management
│   │   ├── models.py                # ORM models (YouTubeVideo, Article, Digest)
│   │   ├── repoisitory.py           # DB read/write operations
│   │   ├── table_operations.py      # Create/drop tables
│   │   └── check_connection.py      # Connection health check script
│   │
│   └── profiles/
│       └── user_profiles.py         # User interest profile for curation
```

---

## Database Schema

| Table            | Description                                      |
|------------------|--------------------------------------------------|
| `youtube_videos` | Raw YouTube video metadata and transcripts       |
| `article`        | Raw articles from OpenAI and Anthropic RSS feeds |
| `digest`         | LLM-generated summaries of articles and videos   |

---

## Local Development

### Prerequisites
- Docker (for local Postgres)
- Python 3.12+
- `uv` package manager

### Setup

```bash
# Start local PostgreSQL
./docker-up.sh

# Install dependencies
uv sync

# Configure environment
cp .env.example .env  # add your API keys

# Run the pipeline
uv run python -m app.daily_runner
```

### Environment Variables

| Variable            | Description                                                             |
|---------------------|-------------------------------------------------------------------------|
| `DATABASE_URL`      | Full PostgreSQL connection string (takes priority over individual vars) |
| `POSTGRES_USER`     | Local DB user                                                           |
| `POSTGRES_PASSWORD` | Local DB password                                                       |
| `POSTGRES_HOST`     | Local DB host (default: `localhost`)                                    |
| `POSTGRES_PORT`     | Local DB port (default: `5432`)                                         |
| `POSTGRES_DB`       | Local DB name                                                           |
| `OPENAI_API_KEY`    | OpenAI API key                                                          |
| `MY_EMAIL`          | Gmail address to send digest from/to                                    |
| `APP_PASSWORD`      | Gmail app password                                                      |

---

## Deployment (Render)

The project deploys to [Render](https://render.com) as a **cron job** using Docker.

- **Schedule:** daily at midnight EDT
- **Database:** Render managed PostgreSQL (free tier)
- **Config:** `render.yaml`

On first run, the pipeline automatically creates all database tables via SQLAlchemy's `create_all`.

Environment variables (`OPENAI_API_KEY`, `MY_EMAIL`, `APP_PASSWORD`) are configured in the Render dashboard and marked `sync: false` in `render.yaml` so they are never committed to the repo.

---

## Adding a New Scraper

The scraper system is designed to be extended. Here's how to add a new article source — using Google Gemini as an example.

### 1. Find the RSS feed

Most blogs have an RSS feed. For Google Gemini/DeepMind:
```
https://blog.google/technology/ai/rss/
```
Check the source's website or try appending `/rss`, `/rss.xml`, or `/feed` to the blog URL.

### 2. Create the scraper class

Create `app/scrapers/gemini_scraper.py` by subclassing `ArticleScraper`:

```python
from app.scrapers.article import Article, ArticleScraper


class GeminiArticleScraper(ArticleScraper):
    def __init__(self):
        super().__init__(
            rss_urls=[
                "https://blog.google/technology/ai/rss/",
            ]
        )

    def get_articles(self, hours: int = 24) -> list[Article]:
        return super().get_articles(hours=hours, source="Gemini")
```

If the source has multiple feeds (like Anthropic), pass them all in the `rss_urls` list.

### 3. Wire it into the runner

In `app/runner.py`, import and call your new scraper alongside the existing ones:

```python
from app.scrapers.gemini_scraper import GeminiArticleScraper

def run_scrapers(hours: str = 24):
    # ... existing scrapers ...

    gemini_scraper = GeminiArticleScraper()
    gemini_articles = gemini_scraper.get_articles(hours=hours)
    logger.info(f"Found {len(gemini_articles)} Gemini articles")
    bulk_insert_articles(articles=gemini_articles)

    return {
        "youtube": videos,
        "anthropic": anthropic_articles,
        "openai": openai_articles,
        "gemini": gemini_articles,  # add to return dict
    }
```

### 4. Update the digest query (if needed)

In `app/database/repoisitory.py`, the `get_undigested_articles` function filters which sources get digested. Add your new source:

```python
articles: list[ArticleSchema] = (
    session.query(ArticleSchema)
    .filter(
        or_(
            ArticleSchema.source == "OpenAI",
            ArticleSchema.source == "Gemini",  # add this
            and_(
                ArticleSchema.source == "Anthropic",
                ArticleSchema.markdown.isnot(None),
            ),
        )
    )
    .all()
)
```

> **Note:** Anthropic requires `markdown` to be populated first because its articles need full content fetching. OpenAI and most other sources work from the RSS description alone, so they don't need this extra step.

### 5. That's it

The rest of the pipeline (digest generation, curation, email) picks up the new articles automatically — no other changes needed.
