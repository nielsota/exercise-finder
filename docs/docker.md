# Docker Guide

## Running the App

```bash
# Start the app with hot-reload
docker compose up

# Rebuild after changing dependencies
docker compose build
docker compose up

# Stop
docker compose down
```

That's it! The app runs at **http://localhost:8000**

---

## Hot-Reload

When you edit files in `src/`, the container auto-reloads within 1-2 seconds.

If hot-reload isn't working:
```bash
docker compose down
docker compose build
docker compose up
```

---

## Environment Variables

Required in `.env`:
```bash
OPENAI_API_KEY=sk-...
SESSION_SECRET_KEY=your-secret-key
AUTH_PASSWORD=your-password
EXAMS_ROOT=data/questions-images
```

---

## Deployment

For AWS deployment, use:
```bash
./scripts/deploy.sh
```
