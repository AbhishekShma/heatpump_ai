# Agent V3 - LiveKit Voice Agent with Frontend & Backend

Complete setup for a LiveKit voice agent with turn detection, token server backend, and React frontend.

## Structure

```
agent_v3/
├── livekit_voice_agent/  # Main agent code
├── token_server/          # FastAPI backend for token generation
└── frontend/              # React frontend application
```

## Setup Instructions

### 1. Agent Setup

The agent is already configured with turn detection enabled. It will work in dev/production mode even if `download-files` fails locally.

```bash
cd livekit_voice_agent
uv run agent.py dev
```

### 2. Backend Token Server

Start the FastAPI token server:

```bash
cd token_server
uv run token_server.py
```

The server will run on `http://localhost:8000` and provide tokens at `/token` endpoint.

### 3. Frontend

Install dependencies and start the frontend:

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:5173`.

## Environment Variables

All components load environment variables from the root-level `.env` file (`d:\projects\heatpump_ai\.env`):

```
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
LIVEKIT_URL=wss://your-project.livekit.cloud
OPENAI_API_KEY=your_openai_api_key  # Required for OpenAI Realtime API
```

## Running Everything

1. **Terminal 1** - Start the agent:
   ```bash
   cd agent_v3/livekit_voice_agent
   uv run agent.py dev
   ```

2. **Terminal 2** - Start the token server:
   ```bash
   cd agent_v3/token_server
   uv run token_server.py
   ```

3. **Terminal 3** - Start the frontend:
   ```bash
   cd agent_v3/frontend
   npm run dev
   ```

4. Open `http://localhost:5173` in your browser and click the microphone button to start talking to the agent!

## Features

- ✅ OpenAI Realtime API with built-in turn detection, STT, LLM, and TTS
- ✅ No local model downloads required - everything runs via API
- ✅ FastAPI backend for token generation
- ✅ React frontend with LiveKit components
- ✅ Audio visualizer showing agent state
- ✅ Microphone controls

## Notes

- Uses OpenAI Realtime API which includes all components (STT, LLM, TTS, turn detection) - no local models needed
- Requires `OPENAI_API_KEY` environment variable to be set
- The agent name is set to `"assistant"` - make sure this matches in both the agent code and token server metadata
- CORS is configured to allow requests from `localhost:5173` (frontend) and `localhost:8000` (backend)
- Voice can be changed in `agent.py` - available voices: alloy, echo, fable, onyx, nova, shimmer, coral (default)

