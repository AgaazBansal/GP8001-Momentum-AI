# GP8001 — Momentum AI

A locally running meeting-minutes prototype for GP8001. Built from
[AgaazBansal/Momentum_AI](https://github.com/AgaazBansal/Momentum_AI).

## Features

- Upload MP3, MP4, WAV or M4A recordings (up to 20 MB).
- Transcribe audio and generate structured minutes using Groq.
- Paste transcripts directly for minutes and transcript-grounded chat.
- Review, delete and manually add discussion points and action items.
- Download minutes as Markdown; optionally export them to Notion.
- Start without API keys in a labelled extractive transcript demo mode.

## Run locally in VS Code

See [LOCAL_SETUP.md](LOCAL_SETUP.md) for complete Windows instructions.
Use Python 3.12 and Node.js 22 LTS. Open two terminals:

**Backend** — from the project root in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --reload
```

**Frontend** — from the project root in a second terminal:

```powershell
cd frontend
npm.cmd ci
npm.cmd start
```

Open http://localhost:3000. The backend runs at http://localhost:8000.
Both servers run on your laptop; no deployment is needed.

## Configuration

Add your own `GROQ_API_KEY` to `backend/.env` and restart the backend for real
AI processing. Audio/transcripts are sent to Groq; this is not an offline LLM.
The model IDs are configurable. Defaults:

```dotenv
SUMMARY_MODEL=openai/gpt-oss-20b
CHAT_MODEL=openai/gpt-oss-20b
TRANSCRIPTION_MODEL=whisper-large-v3
```

Without a key, click **Load sample transcript → Process Transcript** to test
extractive excerpts and keyword search. Demo mode does not automatically extract
action items or assess sentiment. Notion credentials are optional.

Never commit actual API keys or `.env` files. Only `.env.example` templates are
included. Installed dependencies and virtual environments are excluded.

## Validation and limitations

Five backend tests, the React transcript workflow test, and the frontend build
passed in the recovery environment. The user also confirmed that the short sample
and a 12-line, three-person transcript process successfully through Groq locally.
A longer transcript failed; the exact provider error remains unresolved. Use short
transcripts for the current demonstration. Live Notion export remains unverified.

Chat supplies the transcript directly to the model. Vector retrieval, speaker
identification, and conversation memory are not implemented. The existing Create
React App stack is retained and contains older dependencies.

Backend tests, from the project root:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s backend\tests -v
```

Frontend checks, from `frontend`:

```powershell
npm.cmd test -- --watchAll=false --runInBand
npm.cmd run build
```
