# Social Mind

A web application for "Mind in Low Light" - a social media content management system for ADHD/mental health creators.

## Features (v1)

- 📊 **Analytics Dashboard** - Upload TikTok/YouTube CSVs, visualize performance, identify patterns
- 📝 **Hook Generator** - Generate 5-7 hooks instantly for any topic
- 📅 **Content Calendar** - Schedule posts, track status, add notes

## Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Frontend:** React 18 + Vite + Tailwind CSS + Recharts
- **Proxy:** Caddy
- **Deployment:** Docker Compose

## URLs

- Internal (Tailscale): https://social.voidnode.dev
- Local Development: http://localhost:8080

## Setup

```bash
# Development
docker-compose up --build

# Production
docker-compose -f docker-compose.prod.yml up -d
```

## Project Structure

```
social-mind/
├── backend/          # FastAPI application
├── frontend/         # React application
├── caddy/           # Caddy configuration
├── docker/          # Docker files
└── docker-compose.yml
```
