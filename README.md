# Cognizance AI Assistant

AI-powered chatbot backend for Cognizance 2026 — IIT Roorkee's Annual Technical Festival.

Powered by Google Gemini (free tier).

## Features

- **Festival Q&A** — answers questions about events, registration, dates, prizes, workshops, performers, and more using Cognizance festival data baked into the system prompt
- **Issue Troubleshooting** — when a user reports a problem, the agent suggests 3–4 practical fixes and directs them to the dev team email if the issue persists
- **Multi-model Fallback** — tries the primary Gemini model first, then falls back through a configurable list of models if rate-limited
- **Retry with Exponential Backoff** — retries each model up to 3 times (1 s → 2 s → 4 s) on transient quota/rate-limit errors before moving to the next fallback
- **Per-IP Rate Limiting** — 15 requests/minute per IP via slowapi to prevent abuse
- **Chat History** — accepts conversation history from the frontend for multi-turn context (stateless; no server-side session storage)
- **CORS Support** — configurable allowed origins for frontend integration
- **Interactive Docs** — auto-generated Swagger UI and ReDoc

## Project Structure

```
Agent/
├── agent/
│   ├── __init__.py          # Package exports
│   └── agent.py             # CognizanceAgent — prompt, history, Gemini calls, retries
├── api/
│   ├── __init__.py
│   └── routes.py            # FastAPI routes + rate limiter
├── data/
│   ├── __init__.py
│   └── cognizance_data.py   # Festival information (events, dates, theme, etc.)
├── main.py                  # FastAPI app entry point, CORS & rate-limit middleware
├── config.py                # Pydantic Settings (env vars)
├── requirements.txt
├── .env.example
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.9+
- A Google API key (free — get one at [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

```bash
cd Agent
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
GOOGLE_API_KEY=your_key_here
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

| Variable                 | Description                         | Default                                                   |
| ------------------------ | ----------------------------------- | --------------------------------------------------------- |
| `API_HOST`               | Server host                         | `0.0.0.0`                                                 |
| `API_PORT`               | Server port                         | `8000`                                                    |
| `GOOGLE_API_KEY`         | Gemini API key                      | — (required)                                              |
| `GOOGLE_MODEL`           | Primary Gemini model                | `gemini-2.5-flash`                                        |
| `GOOGLE_FALLBACK_MODELS` | Comma-separated fallback models     | `gemini-2.0-flash,gemini-1.5-flash,gemini-2.0-flash-lite` |
| `LLM_TEMPERATURE`        | Response randomness                 | `0.7`                                                     |
| `MAX_TOKENS`             | Max output tokens                   | `2000`                                                    |
| `CORS_ORIGINS`           | Allowed frontend origins            | `http://localhost:3000`                                   |
| `DEBUG`                  | Enable hot reload & verbose logging | `true`                                                    |

### Run

```bash
python main.py
```

Server starts at `http://localhost:8000`.

## API Endpoints

### POST /api/v1/chat

Send a message and optional chat history. Rate limited to 15 req/min per IP.

**Request:**

```json
{
  "message": "What is Cognizance?",
  "chat_history": [
    { "role": "user", "content": "Hello" },
    {
      "role": "assistant",
      "content": "Hi! How can I help you with Cognizance?"
    }
  ]
}
```

**Response:**

```json
{
  "success": true,
  "response": "Cognizance is the annual technical festival of IIT Roorkee...",
  "error": null
}
```

### GET /api/v1/info

Returns basic festival details without a chat interaction.

```json
{
  "festival_name": "Cognizance",
  "edition": "Cognizance'2026",
  "dates": "13th - 15th March 2026",
  "institution": "IIT Roorkee",
  "prize_pool": "50 Lacs INR",
  "theme": "Empyrean Technogenesis",
  "website": "https://www.cognizance.org.in",
  "registration_url": "https://www.cognizance.org.in/events"
}
```

### GET /api/v1/health

```json
{
  "status": "healthy",
  "service": "Cognizance AI Assistant",
  "version": "1.0.0"
}
```

## How It Works

1. The frontend sends the user's message along with the full chat history (stored in session storage on the client).
2. `CognizanceAgent.process_query()` builds Gemini-compatible `Content` objects from the history and the new message.
3. The request is sent to the primary Gemini model. On rate-limit errors it retries with exponential backoff (up to 3 attempts), then moves to the next fallback model.
4. The plain-text response is returned to the frontend. No server-side session state is stored — each request is self-contained.

### Conversation Summary Caching

- Long conversations are automatically summarized in the background and a short 2–3 sentence summary is cached per `conversation_id` to reduce token usage.
- Cached summaries expire after 6 hours (TTL) and are refreshed when necessary. The cache is in-memory by default; for multi-instance deployments replace it with Redis and set an appropriate TTL/eviction policy.

### Error Handling Flow

```
Incoming request
  → Per-IP rate limit check (15/min)
    → Primary model (3 retries with backoff)
      → Fallback model 1 (3 retries)
        → Fallback model 2 (3 retries)
          → Fallback model 3 (3 retries)
            → "All models exhausted, try again later"
```

## Agent Behavior

- Conversational, plain-text responses (no markdown formatting)
- When a user reports an issue, provides 3–4 actionable fixes
- Always directs users to **info-cogn@iitr.ac.in** for unresolved issues
- Covers: events, registration, schedule, prizes, workshops, past performers, theme, and general festival info

## Development

### Updating Festival Data

Edit `data/cognizance_data.py` with new events, dates, or details. The system prompt is rebuilt on server restart.

### Customizing the Agent Prompt

Edit `_create_system_prompt()` in `agent/agent.py`.

### Adjusting Rate Limits

Change the `@limiter.limit("15/minute")` decorator in `api/routes.py`.

### Adjusting Retry Behavior

Change `self.max_retries` and `self.base_retry_delay` in `agent/agent.py`.

## Deployment

### Production

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## Interactive Docs

Once running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Troubleshooting

1. **Import errors** — run `pip install -r requirements.txt`
2. **CORS errors** — add your frontend URL to `CORS_ORIGINS` in `.env`
3. **API key errors** — verify `GOOGLE_API_KEY` is set correctly
4. **Rate limit 429 from Gemini** — the agent retries automatically; if all models are exhausted, wait a few minutes

---

**Cognizance 2026** — Empyrean Technogenesis | 13th–15th March 2026 | IIT Roorkee
# cogni-agent
# cogni-agent
