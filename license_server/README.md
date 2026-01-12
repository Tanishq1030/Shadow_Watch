# Shadow Watch License Server

A FastAPI-based license server running on Vercel.
Architecture: **Redis (Hot)** + **CockroachDB (Cold/System of Record)**.

## 🚀 Setup Guide

### 1. Database Setup (CockroachDB)

1.  Log in to [CockroachDB Cloud](https://cockroachlabs.cloud).
2.  Create a "Serverless" cluster (Free Forever).
3.  Click **"Connect"**.
4.  Select **"General Connection String"**.
5.  Copy the connection string. It will look like this:
    ```
    postgresql://username:password@aws-us-east-1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full
    ```

### 2. Environment Variables

Set these in **Vercel Project Settings** or `.env.local`:

```bash
# Redis (Vercel KV or Redis Cloud)
REDIS_URL="redis://default:password@visual-gull-38292.upstash.io:38292"

# CockroachDB (Primary Database)
# Note: Use 'postgresql://' prefix. If it says 'postgres://', change it to 'postgresql://' for SQLAlchemy.
PLANETSCALE_URL="postgresql://username:password@aws-us-east-1.cockroachlabs.cloud:26257/shadowwatch?sslmode=verify-full"
```
*(We reuse `PLANETSCALE_URL` variable name to avoid code changes, or you can rename it to `DATABASE_URL` in code).*

### 3. Local Development

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Run server:
    ```bash
    uvicorn main:app --reload
    ```
3.  The database will initialize automatically on first run.

## 📡 API Endpoints

-   `POST /trial`: Generate 30-day trial (Users + Redis + DB Log)
-   `POST /verify`: Verify license (Redis only - Fast)
-   `POST /report`: Report usage stats (Redis -> DB sync pending)
-   `GET /stats`: View platform statistics

## 📦 Deployment

```bash
vercel --prod
```
