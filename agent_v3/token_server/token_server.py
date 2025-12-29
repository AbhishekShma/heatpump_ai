"""
Token server for generating LiveKit access tokens.

This FastAPI server generates access tokens for frontend clients to connect
to LiveKit rooms and request agent dispatch.
"""

from dotenv import load_dotenv
from livekit import api
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json

# Load environment variables from root-level .env file
load_dotenv()

app = FastAPI()

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/token")
def token():
    """
    Generate a LiveKit access token.
    
    Returns:
        dict: Contains 'token' (JWT string) and 'url' (LiveKit WebSocket URL)
    """
    print("USING LIVEKIT_URL =", os.environ["LIVEKIT_URL"], flush=True)
    
    token = (
        api.AccessToken(
            os.environ["LIVEKIT_API_KEY"],
            os.environ["LIVEKIT_API_SECRET"],
        )
        .with_identity("browser-user")
        .with_name("Browser User")
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room="test-room",
            )
        )
    )
    
    return {
        "token": token.to_jwt(),
        "url": os.environ["LIVEKIT_URL"],
    }


@app.post("/dispatch-agent")
async def dispatch_agent():
    """
    Explicitly dispatch the agent to the room.
    This is required for named agents.
    
    Returns:
        dict: Success status
    """
    try:
        # Create LiveKit API client
        lkapi = api.LiveKitAPI(
            os.environ["LIVEKIT_URL"],
            os.environ["LIVEKIT_API_KEY"],
            os.environ["LIVEKIT_API_SECRET"],
        )
        
        # Dispatch agent to room
        dispatch = await lkapi.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name="assistant",
                room="test-room",
            )
        )
        
        print(f"Agent dispatched to test-room: {dispatch}")
        await lkapi.aclose()
        return {"success": True, "message": "Agent dispatched"}
    except Exception as e:
        print(f"Error dispatching agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


