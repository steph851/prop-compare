# Prop Firm Intelligence System

AI-powered platform for comparing prop trading firms — evaluating challenges, rules, payouts, and more.

## Features

- **Multi-Agent AI System** — 6 specialized agents for discovery, research, extraction, validation, monitoring
- **40+ Trading Challenges Analyzed** — Apex, FundedNext, Topstep, Tradeify, Lucid, and more
- **Real-time Dashboard** — Interactive comparison tool with scoring engine
- **Automated Monitoring** — Tracks rule changes and updates across firms
- **Decision Audit Trail** — Full logging of all system decisions

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the pipeline for a specific firm
python run.py pipeline fundednext

# Start the API server
python api.py
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Dashboard UI |
| `GET /api/firms` | List all tracked firms |
| `GET /api/firm/{name}` | Get firm details |
| `GET /api/comparison` | Full comparison data |
| `GET /api/decisions` | Audit log |
| `GET /health` | Health check |

## Deployment

Deploy to Render using the included `render.yaml` blueprint.

## Tech Stack

- Python (FastAPI, Anthropic SDK)
- Vue 3 + Tailwind CSS (dashboard)
- Multi-agent AI architecture
- PostgreSQL-ready data models

## License

MIT