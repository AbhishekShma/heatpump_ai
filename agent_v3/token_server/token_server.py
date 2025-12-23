"""
Token server for generating LiveKit access tokens.

This FastAPI server generates access tokens for frontend clients to connect
to LiveKit rooms and request agent dispatch.
"""

from dotenv import load_dotenv
from livekit import api
from fastapi import FastAPI
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
    Generate a LiveKit access token with agent dispatch metadata.
    
    Returns:
        dict: Contains 'token' (JWT string) and 'url' (LiveKit WebSocket URL)
    """
    meta = {
        "lk.agent.request": True,
        "lk.agent.name": "assistant",
    }
    print("ISSUING TOKEN WITH METADATA:", meta)
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
        .with_metadata(json.dumps({
            "lk.agent.request": True,
            "lk.agent.name": "assistant",
        }))
    )

    return {
        "token": token.to_jwt(),
        "url": os.environ["LIVEKIT_URL"],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


