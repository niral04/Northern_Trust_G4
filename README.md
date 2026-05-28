# Northern Trust G4 - Incident Management System

This project has a FastAPI backend and a React/Vite frontend.

## Important Windows note

If you downloaded the project as a ZIP, Windows may create a nested folder. If `dir` shows only `.venv` and another `Northern_Trust_G4-main` folder, move into the inner project folder first:

```bat
cd Northern_Trust_G4-main
dir
```

You are in the correct folder when `dir` shows files/folders like:

```text
app
backend
frontend
requirements.txt
simulator
```

Run all backend commands from that folder, not from the outer ZIP folder.

## Backend setup on Windows Command Prompt

```bat
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Then open:

```text
http://127.0.0.1:8000/
```

Expected response:

```json
{"message":"IMS Backend Running"}
```

## Frontend setup on Windows Command Prompt

Open a second Command Prompt in the same project folder:

```bat
cd frontend
npm install
set VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

Then open the Vite URL shown in the terminal, usually:

```text
http://localhost:5173/
```

## macOS/Linux setup

Backend:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Frontend:

```bash
cd frontend
npm install
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

## Which backend should I run?

Run the backend in the `app` folder:

```bat
py -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The `backend` folder contains an older alternate implementation. The frontend is wired to the `app` backend endpoints.
