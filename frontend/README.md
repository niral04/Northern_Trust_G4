# Event-Driven Incident Management Frontend

Production-ready React + Vite dashboard scaffold for the hackathon incident system.

## Setup

```bash
cd frontend
npm install
npm run dev
```

Build check:

```bash
npm run build
```

## Stack

- React + Vite
- Tailwind CSS with shadcn/ui-compatible tokens
- React Router
- Recharts
- Lucide React icons
- Framer Motion

## Backend Endpoints

The API layer is ready for:

- `GET /analytics`
- `GET /analytics/stats`
- `GET /incidents`

Set the backend URL with:

```bash
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

When the backend is unavailable, the UI falls back to mock incident data for demo readiness.

## Suggested shadcn Commands

This repository includes compatible local primitives in `src/components/ui`. To add more official shadcn components later:

```bash
npx shadcn@latest add button card badge progress table sheet dropdown-menu tabs
```

## Structure

```text
src/
  components/
    analytics/
    dashboard/
    layout/
    shared/
    ui/
  context/
  lib/
  mock/
  pages/
  routes/
  services/
```
