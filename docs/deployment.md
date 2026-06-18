# Deployment Instructions

This guide covers how to deploy AI News Hub to production on Render.

---

## Prerequisites

- A [Render](https://render.com) account
- Your project pushed to a GitHub or GitLab repository
- An OpenAI API key
- A Gmail account with an App Password set up

---

## First-Time Deployment

### 1. Connect your repository

1. Log in to Render and click **New** -> **Blueprint**
2. Connect your GitHub/GitLab account and select the `ai-news-hub` repository
3. Render will detect `render.yaml` and provision all resources automatically:
   - A managed PostgreSQL database (`ai-news-hub-db`)
   - A cron job service (`daily-digest-job`)

### 2. Set environment variables

After the blueprint is applied, the following variables need to be set manually in the Render dashboard (they are marked `sync: false` in `render.yaml` to keep secrets out of the repo):

| Variable        | Where to find it                                      |
|-----------------|-------------------------------------------------------|
| `OPENAI_API_KEY`| [platform.openai.com](https://platform.openai.com)   |
| `MY_EMAIL`      | Your Gmail address                                    |
| `APP_PASSWORD`  | Gmail -> Manage Account -> Security -> App Passwords  |

`DATABASE_URL` is set automatically by Render from the provisioned database — you do not need to set it manually.

To set variables:
1. Go to your cron job service in the Render dashboard
2. Click **Environment**
3. Add each variable and click **Save Changes**

### 3. Trigger a manual run

Before waiting for the scheduled time, trigger a manual run to verify everything works:

1. Go to the cron job service
2. Click **Trigger Run**
3. Watch the logs — the pipeline should complete all 5 steps and send an email

---

## Redeployment

Every `git push` to your main branch triggers an automatic redeploy. Render rebuilds the Docker image and the next cron run will use the new code.

To force an immediate redeploy without a code change:
1. Go to the cron job service in the Render dashboard
2. Click **Manual Deploy** -> **Deploy latest commit**

---

## Cron Schedule

The schedule is defined in `render.yaml`:

```yaml
schedule: "0 4 * * *"  # midnight EDT (04:00 UTC)
```

Render uses UTC. To change the time, update `render.yaml` and push. Use this conversion:

| Your timezone | Offset | Midnight local = UTC |
|---------------|--------|----------------------|
| EDT (summer)  | UTC-4  | 04:00                |
| EST (winter)  | UTC-5  | 05:00                |

---

## Checking Logs

1. Go to your cron job service on Render
2. Click **Logs** in the left sidebar
3. Each run shows timestamped output from the pipeline

---

## Database

The pipeline automatically creates all required tables on first run via SQLAlchemy's `create_all`. No manual migrations are needed for a fresh deployment.

To verify the database is reachable, run the connection check script locally with `DATABASE_URL` pointing at the Render DB:

```bash
cd ai-news-hub && .venv/bin/python app/database/check_connection.py
```
