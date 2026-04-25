# Social Mind

A web application for "Mind in Low Light" - a social media content management system for creators.

## Features (v1)

- 📊 **Analytics Dashboard** - Upload TikTok/YouTube CSVs, visualize performance, identify patterns
- 📝 **Hook Generator** - Generate hooks instantly for any topic (5 tones: professional, casual, dramatic, funny, inspirational)
- 📅 **Content Calendar** - Schedule posts, track status, add notes

## Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite (async)
- **Frontend:** React 18 + Vite + Tailwind CSS + Recharts
- **Proxy:** Caddy
- **Deployment:** Docker Compose

## URLs

- Internal (Tailscale): https://social.voidnode.dev
- Local Development: http://localhost:5173

## Quick Start

```bash
# Clone the repository
git clone https://forgejo.voidnode.dev/nuno/social-mind.git
cd social-mind

# Set up environment
cp .env.example .env
# Edit .env and set a secure SECRET_KEY!

# Build and run
cd docker
docker-compose up -d
```

## Development Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Create data directory
mkdir -p data uploads
# Run development server
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
social-mind/
├── backend/
│   ├── app/
│   │   ├── core/          # Config, database, enums
│   │   ├── models/        # SQLAlchemy models
│   │   ├── routers/       # API endpoints (analytics, hooks, calendar)
│   │   └── main.py        # FastAPI entry point
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Dashboard, Hooks, Calendar
│   │   └── services/      # API client
│   └── package.json
├── docker/
│   ├── docker-compose.yml
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
├── caddy/
│   └── Caddyfile
└── .env.example
```

## Security Notes

- **SECRET_KEY**: MUST be changed in production! Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- File uploads are limited to 10MB
- Path traversal protection on file uploads
- CORS origins should be restricted in production

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/analytics/upload` - Upload CSV analytics
- `GET /api/analytics/summary` - Get analytics summary
- `GET /api/hooks/` - List generated hooks
- `POST /api/hooks/generate` - Generate new hooks
- `GET /api/calendar/` - List calendar items
- `POST /api/calendar/` - Create calendar item

## Deployment

1. Set `SECRET_KEY` in `.env`
2. Run `docker-compose up -d` in the `docker/` directory
3. Caddy will automatically get TLS certificates
4. Access at https://social.voidnode.dev (Tailscale required)

## Development Status

✅ Code review complete - all critical issues fixed
✅ Security vulnerabilities patched
✅ ESLint with a11y configured
✅ TypeScript compilation passing
✅ Git repo clean (node_modules excluded)

### Recent Fixes:
- Backend now uses proper async database engine with lifespan manager
- Added file path sanitization to prevent path traversal
- Added chunked file reading with 10MB size limit
- Replaced hardcoded SECRET_KEY with secrets.token_urlsafe()
- Standardized datetime usage to UTC with timezone
- Added Platform, ContentType, Tone, CalendarStatus enums
- Created src/services/api.ts with Axios config
- Removed unused imports (PieChart, Pie, Cell)
- Added null check for root element in main.tsx
- Added ESLint config with a11y support
- Added accessibility labels to charts (aria-label, role, sr-only text)
- Cleaned node_modules from git history

## License

MIT - For internal Mind in Low Light use
