# Agent V3 - LiveKit Voice Agent with Token Server

Complete setup for a LiveKit voice agent with turn detection and token server backend.

## Structure

```
agent_v3/
├── livekit_voice_agent/  # Main agent code
└── token_server/          # FastAPI backend for token generation
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

The token server will be available at `http://localhost:8000/token` for generating LiveKit access tokens.

## Features

- ✅ OpenAI Realtime API with built-in turn detection, STT, LLM, and TTS
- ✅ No local model downloads required - everything runs via API
- ✅ FastAPI backend for token generation
- ✅ Agent name configured as "assistant" for explicit dispatch

## Notes

- Uses OpenAI Realtime API which includes all components (STT, LLM, TTS, turn detection) - no local models needed
- Requires `OPENAI_API_KEY` environment variable to be set
- The agent name is set to `"assistant"` in both `agent.py` (via `@server.rtc_session(agent_name="assistant")`) and token server metadata - they must match
- CORS is configured in the token server to allow requests from common localhost ports
- Voice can be changed in `agent.py` - available voices: alloy, echo, fable, onyx, nova, shimmer, coral (default)

