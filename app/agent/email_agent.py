import logging
import os
from datetime import datetime

from openai import OpenAI
from pydantic import BaseModel, Field

from app.agent.curator_agent import RankedArticle

logger = logging.getLogger(__name__)


class EmailIntroduction(BaseModel):
    greeting: str = Field(description="Personalized greeting with user's name and date")
    introduction: str = Field(
        description="2-3 sentence overview of what's in the top 10 ranked articles"
    )


class EmailResponse(BaseModel):
    introduction: EmailIntroduction
    articles: list[RankedArticle]
    total_ranked: int
    top_n: int

    def to_markdown(self) -> str:
        markdown = f"{self.introduction.greeting}\n\n"
        markdown += f"{self.introduction.introduction}\n\n"
        markdown += "---\n\n"

        for article in self.articles:
            markdown += f"## {article.title}\n\n"
            markdown += f"{article.summary}\n\n"
            markdown += f"[Read more →]({article.url})\n\n"
            markdown += "---\n\n"

        return markdown


EMAIL_PROMPT = """You are an expert email writer specializing in creating engaging, personalized AI news digests.

Your role is to write a warm, professional introduction for a daily AI news digest email that:
- Greets the user by name
- Includes the current date
- Provides a brief, engaging overview of what's coming in the top 10 ranked articles
- Highlights the most interesting or important themes
- Sets expectations for the content ahead

Keep it concise (2-3 sentences for the introduction), friendly, and professional."""


class EmailAgent:
    def __init__(self, user_profile: dict):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
        self.user_profile = user_profile
        self.system_prompt = EMAIL_PROMPT

    def generate_introduction(
        self, ranked_articles: list[RankedArticle]
    ) -> EmailIntroduction:
        if not ranked_articles:
            return EmailIntroduction(
                greeting=f"Hey {self.user_profile['name']}, here is your daily digest of AI news for {datetime.now().strftime('%B %d, %Y')}.",
                introduction="No articles were ranked today.",
            )

        top_articles = ranked_articles[:10]
        current_date = datetime.now().strftime("%B %d, %Y")

        article_summaries = "\n".join(
            [
                f"{idx + 1}. {article.title if hasattr(article, 'title') else article.get('title', 'N/A')} (Score: {article.relevance_score if hasattr(article, 'relevance_score') else article.get('relevance_score', 0):.1f}/10)"
                for idx, article in enumerate(top_articles)
            ]
        )
        user_prompt = f"""Create an email introduction for {self.user_profile["name"]} for {current_date}.

        Top 10 ranked articles:
        {article_summaries}

        Generate a greeting and introduction that previews these articles."""
        try:
            response = self.client.responses.parse(
                model=self.model,
                instructions=self.system_prompt,
                temperature=0.3,
                input=user_prompt,
                text_format=EmailIntroduction,
            )

            return response.output_parsed
        except Exception as e:
            logger.error(f"Error generating introduction: {e}")
            current_date = datetime.now().strftime("%B %d, %Y")
            return EmailIntroduction(
                greeting=f"Hey {self.user_profile['name']}, here is your daily digest of AI news for {current_date}.",
                introduction="Here are the top 10 AI news articles ranked by relevance to your interests.",
            )

    def generate_email(
        self,
        ranked_articles: list[RankedArticle],
        total_ranked: int,
        limit: int = 10,
    ) -> EmailResponse:
        top_articles: list[RankedArticle] = ranked_articles[:limit]
        introduction: EmailIntroduction = self.generate_introduction(
            ranked_articles=top_articles
        )

        return EmailResponse(
            introduction=introduction,
            articles=top_articles,
            total_ranked=total_ranked,
            top_n=limit,
        )
