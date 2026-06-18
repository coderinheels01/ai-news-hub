# Render Setup Guide

This guide explains the Render infrastructure for AI News Hub and how to configure it from scratch.

---

## Overview

AI News Hub uses two Render resources, both defined in `render.yaml`:

| Resource         | Type            | Plan  | Purpose                        |
|------------------|-----------------|-------|--------------------------------|
| `ai-news-hub-db` | PostgreSQL DB   | Free  | Stores videos, articles, digests |
| `daily-digest-job` | Cron Job      | Free  | Runs the pipeline daily        |

---

## render.yaml Explained

```yaml
databases:
  - name: ai-news-hub-db       # Internal Render name
    databaseName: ai_news_hub  # Actual PostgreSQL database name
    user: ainewshub            # PostgreSQL user
    plan: free

services:
  - type: cron
    name: daily-digest-job
    env: docker                # Uses the Dockerfile to build the image
    dockerfilePath: ./Dockerfile
    schedule: "0 4 * * *"     # Runs at 04:00 UTC (midnight EDT)
    dockerCommand: python main.py
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: ai-news-hub-db
          property: connectionString  # Auto-injected by Render
      - key: OPENAI_API_KEY
        sync: false            # Must be set manually in the dashboard
      - key: MY_EMAIL
        sync: false
      - key: APP_PASSWORD
        sync: false
```

---

## PostgreSQL Database

### Connection strings
Render provides two connection strings — use the right one depending on context:

| Type     | When to use                                      |
|----------|--------------------------------------------------|
| Internal | From services running inside Render (cron job)   |
| External | From your local machine (debugging, check_connection.py) |

The external URL requires `?sslmode=require` appended. Find both in:
**Render Dashboard** -> your database -> **Connections** tab

### Free tier limits
- 1 GB storage
- 97 days expiry (database is deleted after 97 days of inactivity — Render will email you before this happens)
- Max 97 connections

---

## Cron Job Service

### How it works
1. Render builds a Docker image from your `Dockerfile`
2. At the scheduled time, it runs `python main.py` inside the container
3. The container exits when the script completes
4. Logs are available in the Render dashboard for each run

### Networking
The cron job runs inside Render's private network, so it connects to the database via the internal connection string (injected automatically via `DATABASE_URL`).

### Inbound IP restrictions
By default, Render allows `0.0.0.0/0` (all IPs) for the database. If you want to restrict access to only Render's network, you can remove this rule — but you would then lose the ability to connect from your local machine.

---

## Gmail App Password Setup

The pipeline sends email via Gmail SMTP. A regular Gmail password won't work — you need an App Password:

1. Go to your Google Account -> **Security**
2. Enable **2-Step Verification** if not already enabled
3. Go to **Security** -> **App Passwords**
4. Select app: **Mail**, device: **Other** (name it "AI News Hub")
5. Copy the 16-character password
6. Set it as `APP_PASSWORD` in the Render dashboard

---

## Monitoring

- **Logs:** Render dashboard -> cron job service -> **Logs**
- **Run history:** Shows each scheduled and manual run with status (success/failed)
- **Alerts:** Configure email alerts in Render dashboard -> your service -> **Notifications**

---

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Connection timeout from local machine | VPN blocking port 5432 | Disconnect VPN |
| `relation does not exist` | Tables not created yet | Run `daily_runner.py` once or trigger a manual run |
| Cron job not running | `render.yaml` not pushed | Commit and push `render.yaml` changes |
| No logs visible | Python output buffered | `PYTHONUNBUFFERED=1` is set in Dockerfile — ensure it's present |
| Email not sending | Wrong App Password | Regenerate App Password in Google Account settings |
