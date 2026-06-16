import html
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import markdown
from dotenv import load_dotenv

from app.agent.email_agent import EmailResponse

load_dotenv()

MY_EMAIL = os.getenv("MY_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")


def send_email(
    subject: str,
    body_text: str,
    body_html: str = None,
    recipients: list = None,
    save_to_file: bool = False,
):
    if recipients is None:
        if not MY_EMAIL:
            raise ValueError("MY_EMAIL environment variable is not set")
        recipients = [MY_EMAIL]
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = MY_EMAIL
    msg["To"] = ", ".join(recipients)

    part1 = MIMEText(body_text, "plain")
    msg.attach(part1)

    if body_html:
        part2 = MIMEText(body_html, "html")
        msg.attach(part2)

    if save_to_file:
        # Save to file instead of sending
        filename = f"email_{subject.replace(' ', '_')}.html"
        with open(filename, "w") as f:
            f.write(f"Subject: {subject}\n")
            f.write(f"From: {MY_EMAIL}\n")
            f.write(f"To: {', '.join(recipients)}\n")
            f.write("---\n\n")
            f.write(body_html if body_html else body_text)
        print(f"Email saved to {filename}")
        return

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(MY_EMAIL, APP_PASSWORD)
        smtp.sendmail(MY_EMAIL, recipients, msg.as_string())


def digest_to_html(digest_response: EmailResponse) -> str:

    html_parts = []
    greeting_html = markdown.markdown(
        digest_response.introduction.greeting, extensions=["extra", "nl2br"]
    )
    introduction_html = markdown.markdown(
        digest_response.introduction.introduction, extensions=["extra", "nl2br"]
    )
    html_parts.append(f'<div class="greeting">{greeting_html}</div>')
    html_parts.append(f'<div class="introduction">{introduction_html}</div>')
    html_parts.append("<hr>")

    for article in digest_response.articles:
        html_parts.append(f"<h3>{html.escape(article.title)}</h3>")
        summary_html = markdown.markdown(article.summary, extensions=["extra", "nl2br"])
        html_parts.append(f"<div>{summary_html}</div>")
        html_parts.append(
            f'<p><a href="{html.escape(article.url)}" class="article-link">Read more →</a></p>'
        )
        html_parts.append("<hr>")

    html_content = "\n".join(html_parts)

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
        }}
        h3 {{
            font-size: 16px;
            font-weight: 600;
            color: #1a1a1a;
            margin-top: 20px;
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        p {{
            margin: 8px 0;
            color: #4a4a4a;
        }}
        strong {{
            font-weight: 600;
            color: #1a1a1a;
        }}
        em {{
            font-style: italic;
            color: #666;
        }}
        a {{
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        hr {{
            border: none;
            border-top: 1px solid #e5e5e5;
            margin: 20px 0;
        }}
        .greeting {{
            font-size: 16px;
            font-weight: 500;
            color: #1a1a1a;
            margin-bottom: 12px;
        }}
        .introduction {{
            color: #4a4a4a;
            margin-bottom: 20px;
        }}
        .article-link {{
            display: inline-block;
            margin-top: 8px;
            color: #0066cc;
            font-size: 14px;
        }}
        .greeting p {{
            margin: 0;
        }}
        .introduction p {{
            margin: 0;
        }}
        div {{
            margin: 8px 0;
            color: #4a4a4a;
        }}
        div p {{
            margin: 4px 0;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""


if __name__ == "__main__":
    send_email(
        subject="hello",
        body_text="hey Emily",
        body_html="Hey <strong>Emily</strong>",
        recipients=["emily.aung2017@gmail.com"],
        save_to_file=True,
    )
