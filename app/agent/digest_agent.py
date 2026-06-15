import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.responses.parsed_response import ParsedResponse
from pydantic import BaseModel

load_dotenv()

SYSTEM_PROMPT = """You are an expert AI news analyst specializing in summarizing technical articles, research papers, and video content about artificial intelligence.

Your role is to create concise, informative digests that help readers quickly understand the key points and significance of AI-related content.

Guidelines:
- Create a compelling title (5-10 words) that captures the essence of the content
- Write a 2-3 sentence summary that highlights the main points and why they matter
- Focus on actionable insights and implications
- Use clear, accessible language while maintaining technical accuracy
- Avoid marketing fluff - focus on substance"""


class DigestAgentResponse(BaseModel):
    title: str
    summary: str


class DigestAgent:
    def __init__(self):
        self.client = OpenAI(os.get("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
        self.system_prompt = SYSTEM_PROMPT

    def generate_digest(
        self, title: str, article_type: str, content: str
    ) -> DigestAgentResponse:
        user_prompt: str = f"Create a digest for this {article_type}: \n Title: {title} \n Content: {content[:8000]}"
        response: ParsedResponse = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            text_format=DigestAgentResponse,
        )
        return response.output_parsed
