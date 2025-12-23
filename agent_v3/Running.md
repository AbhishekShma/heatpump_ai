Start the agent: 
cd agent_v3/livekit_voice_agent
uv run agent.py dev

Start the backend: 
cd agent_v3/token_server 
uv run token_server.py

Start the frontend: 
#### npm install
cd agent_v3/frontend 
npm run dev