"""
LiveKit Voice Agent Boilerplate

A minimal voice AI agent using OpenAI Realtime API.
The Realtime API includes built-in STT, LLM, TTS, and turn detection.
Runnable in console mode for testing.
"""

from dotenv import load_dotenv

from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import noise_cancellation, openai

from tools import get_current_time
from prompts import AGENT_INSTRUCTIONS

# Load environment variables from root-level .env file
load_dotenv()


class Assistant(Agent):
    """
    Basic assistant agent with simple instructions.
    """
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTIONS,
            tools=[get_current_time],
        )


server = AgentServer()


@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    """
    Main agent session handler.
    Uses OpenAI Realtime API which includes STT, LLM, TTS, and turn detection.
    """
    session = AgentSession(
        # OpenAI Realtime API includes built-in turn detection, STT, LLM, and TTS
        llm=openai.realtime.RealtimeModel(
            voice="coral"  # You can change this to other voices: alloy, echo, fable, onyx, nova, shimmer
        ),
        # Turn detection is built into OpenAI Realtime API
        turn_detection=None,
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony() 
                if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP 
                else noise_cancellation.BVC(),
            ),
        ),
    )

    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )


if __name__ == "__main__":
    agents.cli.run_app(server)

