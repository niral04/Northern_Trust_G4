```markdown
# Incident Management System

A real-time event-driven incident management platform built for DevOps environments. Automatically detects, classifies, escalates, and resolves infrastructure and application incidents with live dashboard updates.

## Demo
- Fire alerts via simulator
- Watch incidents appear on dashboard in real time
- Slack notifications fire automatically
- Auto-escalation triggers if nobody responds
- Resolve incidents and view post-mortem reports

## Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| Python + FastAPI | Core API and business logic |
| SQLite + SQLAlchemy | Database |
| APScheduler | Auto-escalation background jobs |
| WebSockets | Real-time dashboard updates |
| Slack Webhook | Infrastructure notifications |
| Gmail SMTP | Application notifications |

### Frontend
| Technology | Purpose |
|---|---|
| React | Dashboard UI |
| Tailwind CSS | Styling |
| Recharts | Analytics charts |
| Axios | API calls |
| WebSocket API | Real-time connection |

## Project Structure
```
incident-management/
│
├── backend/
│   ├── main.py                 ← FastAPI entry point + WebSocket
│   ├── database.py             ← SQLite connection
│   ├── models.py               ← Database tables (IST timezone)
│   ├── classifier.py           ← Alert classification engine
│   ├── incident_engine.py      ← Lifecycle + post-mortem generator
│   ├── escalation.py           ← Auto-escalation timer logic
│   ├── notifications.py        ← Slack + Email dispatcher
│   ├── websocket_manager.py    ← WebSocket connection manager
│   ├── requirements.txt        ← Python dependencies
│   ├── .env.example            ← Environment variable template
│   └── routes/
│       ├── alerts.py           ← Alert ingestion endpoints
│       └── incidents.py        ← Incident control endpoints
│
├── frontend/
│   └── src/
│       ├── App.jsx             ← WebSocket state management
│       ├── utils/time.js       ← IST time conversion
│       └── components/
│           ├── Dashboard.jsx   ← Main layout
│           ├── StatsBar.jsx    ← Live stats cards
│           ├── IncidentTable.jsx ← Incidents list + controls
│           ├── IncidentDetail.jsx ← Timeline + post-mortem
│           └── Analytics.jsx  ← Charts and MTTR
│
└── simulator/
    └── alert_simulator.py      ← Fires fake alerts for demo
```

## Features

### Core
- Real-time dashboard via WebSockets (updates every 2 seconds)
- Auto-classification of infrastructure vs application incidents
- Severity levels: Critical, High, Medium, Low
- Full incident lifecycle: Open → Acknowledged → Escalated → Resolved

### Notifications
- Infrastructure incidents → Slack (immediate)
- Application incidents → Email
- Escalation notifications to next person in chain

### Escalation Chain
| Type | Level 0 | Level 1 | Level 2 | Timeout |
|---|---|---|---|---|
| Infrastructure Critical | On-Call Engineer | Senior Engineer | Team Lead | 5 mins |
| Application High | App Support Team | Senior Developer | Team Lead | 20 mins |

### Dashboard
- Live incident table with severity color coding
- Manual controls: Acknowledge, Escalate, Resolve
- Incident timeline showing every event
- Auto-generated post-mortem on resolution
- Analytics: incidents by service, by severity, MTTR tracking
- All times displayed in IST (Indian Standard Time)

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm 9+

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
cp .env.example .env
# Fill in your Slack webhook URL and email credentials
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm start
```

### Simulator
```bash
cd simulator
python alert_simulator.py
```

## Environment Variables
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
EMAIL_SENDER=yourapp@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
EMAIL_RECEIVER=oncall@company.com
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/alerts | Ingest new alert |
| GET | /api/incidents | List all incidents |
| GET | /api/incidents/active | List active incidents |
| GET | /api/incidents/{id} | Get single incident |
| GET | /api/incidents/{id}/timeline | Get event timeline |
| GET | /api/incidents/{id}/postmortem | Get post-mortem report |
| PUT | /api/incidents/{id}/acknowledge | Acknowledge incident |
| PUT | /api/incidents/{id}/escalate | Escalate incident |
| PUT | /api/incidents/{id}/resolve | Resolve incident |
| GET | /api/dashboard/stats | Get dashboard statistics |
| WS | /ws | WebSocket real-time feed |

## Ports
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Dashboard: http://localhost:3000

## Two Incident Types

### Infrastructure (High Priority)
- Server down, network failure, high CPU, disk full
- Notified via Slack immediately
- Escalates every 5 minutes
- Dashboard shows in RED

### Application (Lower Priority)
- Error rate spikes, slow APIs, job failures
- Notified via Email
- Escalates every 20 minutes
- Dashboard shows in YELLOW
```
