from dotenv import load_dotenv
from livekit import api
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import json

load_dotenv(".env")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000","http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/token")
def token():
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
