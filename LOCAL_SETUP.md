# Momentum AI: local setup in VS Code (Windows)

This recovery version is based on AgaazBansal/Momentum_AI, commit 9e49fbe.
It preserves the React UI and FastAPI service. You do not need to retrain a model.
The original backend called hosted Groq models; it did not train them locally.

## 1. Open the project

Extract Momentum_AI_local.zip and open its Momentum_AI folder in VS Code.
The folder should contain backend, frontend, README.md and this guide.
Install Python 3.12 and Node.js 22 LTS if they are not already installed.
Reopen VS Code after installing them so the terminals pick up PATH changes.
The checks for this download ran on Linux with Python 3.12.14 and Node 24.19.0;
Windows commands are provided here, but were not executed on a Windows machine.

## 2. Start the backend

Open a PowerShell terminal in VS Code, at the project root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

Leave this terminal running. Open http://localhost:8000 to see the health response.
Interactive API documentation is at http://localhost:8000/docs.
No activation command is required; this avoids PowerShell execution-policy issues.
If `.env` already exists, preserve it instead of copying over it.
If `py` is unavailable but Python 3.12 is on PATH, use `python -m venv .venv`.

## 3. Start the frontend

Open a second PowerShell terminal at the project root:

```powershell
cd frontend
npm.cmd ci
Copy-Item .env.example .env
npm.cmd start
```

Open http://localhost:3000. Keep both terminals running.
Using npm.cmd avoids the Windows PowerShell restriction on npm.ps1.

## 4. First test: no API keys required

Click **Load sample transcript**, then **Process Transcript**.
You can inspect transcript excerpts, manually add/delete discussion points and
 tasks, ask questions using keyword matching, and download minutes as Markdown.

The banner labels this **demo mode**. It is an extractive interface preview, not
an AI model: it does not assess sentiment or automatically extract action items.
Audio processing and Notion export remain disabled until their credentials exist.
You can paste your own transcript (up to 60,000 characters) too.

## 5. Enable actual AI and audio transcription

Create or retrieve your own key at https://console.groq.com/keys.
Open `backend/.env` and set:

```dotenv
GROQ_API_KEY=your_actual_groq_key
SUMMARY_MODEL=openai/gpt-oss-20b
CHAT_MODEL=openai/gpt-oss-20b
TRANSCRIPTION_MODEL=whisper-large-v3
DEMO_MODE=true
```

Stop the backend with Ctrl+C and start it again using the uvicorn command above.
The banner should now say **Groq AI enabled**. Upload MP3, MP4, WAV or M4A files
(up to 20 MB), or paste transcripts for real AI minutes and chat. Processing audio
uses Whisper on Groq, then the configured chat model to generate the minutes.

With a key configured, the app uses Groq regardless of DEMO_MODE. Invalid keys,
rate limits or model failures produce an error; it does not silently substitute a
demo result. Setting DEMO_MODE=false prevents transcript demo output without a key.
Remove the key and restart to return to demo mode.

Your app runs locally, but audio/transcripts are sent to Groq for AI processing.
This version does not include offline speech recognition or an offline LLM.
Do not put API keys into frontend/.env or commit backend/.env to GitHub.

The old `llama3-8b-8192` model was retired. Its initial replacement
`llama-3.1-8b-instant` was also retired for free/developer accounts in August 2026.
The default above uses the currently documented replacement. You can change
model IDs in `.env` if Groq changes availability again:
https://console.groq.com/docs/deprecations
https://console.groq.com/docs/models

## 6. Optional Notion export

Local use and Markdown download do not need Notion. To enable export, configure:

```dotenv
NOTION_API_KEY=your_notion_integration_token
NOTION_DATABASE_ID=your_database_id
```

Share the database with the integration and restart the backend. This recovery
version keeps the original database-based Notion integration and explicitly uses
Notion API version 2022-06-28. The database must have a title property with API
property key `title`, as expected by the original code. If your title property is
named `Name`, change the `properties={"title": ...}` key in backend/main.py to `Name`.
Live export is not verified without credentials. Very long minutes may exceed
Notion's block/rich-text limits; Markdown download is available for all lengths.

## Troubleshooting

- **Backend unavailable:** verify the first terminal is still running and open
  http://localhost:8000. frontend/.env should use REACT_APP_API_URL=http://localhost:8000.
  Restart the frontend after changing its .env file.
- **Audio disabled:** add the Groq key in backend/.env and restart the backend.
- **Invalid key:** replace your key; its validity cannot be determined from public
  repository code. Keep credentials private.
- **Model unavailable / bad request:** consult Groq's model list, update model IDs
  in backend/.env and restart. For audio, also try a shorter supported file.
- **Quota/rate limit:** wait and retry, or check Groq account limits.
- **Port occupied:** stop the previous process on that port. If the frontend uses
  port 3001, add http://localhost:3001 to CORS_ORIGINS in backend/.env and restart.
- **Python dependency install error:** use a fresh Python 3.12 virtual environment.
  The original large torch/Chroma dependency list is no longer required.
- **npm dependency warnings:** the existing Create React App stack is retained.
  The install/build passed here, but that stack includes older dependencies. A
  Vite migration is outside this minimal local recovery.

## macOS/Linux alternative

From the project root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
.venv/bin/python -m uvicorn main:app --app-dir backend --reload
```

In a second terminal:

```bash
cd frontend
npm ci
cp .env.example .env
npm start
```

## Validation of this recovery

- Clean backend dependency installation and key-free startup passed.
- Five backend tests cover demo processing/chat, absent optional credentials,
  invalid/oversized input, mock-provider audio/JSON output, invalid-key errors,
  and disabled demo behavior.
- The React transcript workflow test and production build passed.
- Live Groq audio/summary/chat and Notion export require your credentials and were
  not exercised. Provider integrations were tested with mocks only.

Run the backend checks from the project root:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s backend\tests -v
```

Run the frontend checks from frontend:

```powershell
npm.cmd test -- --watchAll=false --runInBand
npm.cmd run build
```
