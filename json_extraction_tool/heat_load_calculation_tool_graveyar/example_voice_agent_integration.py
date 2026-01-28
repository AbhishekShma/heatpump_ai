"""
Example: Integrating heat_load_calculation_tool with voice agent (agent_v3)

This shows how to add the tool to the voice agent.
"""

from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import noise_cancellation, openai

from json_extraction_tool import heat_load_calculation_tool
from prompts import AGENT_INSTRUCTIONS  # Your existing prompts

load_dotenv()


class Assistant(Agent):
    """
    Assistant agent with heat load calculation tool.
    """
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTIONS,
            tools=[heat_load_calculation_tool],  # Add the tool here
        )


server = AgentServer()


@server.rtc_session(agent_name="assistant")
async def my_agent(ctx: agents.JobContext):
    """Main agent session handler."""
    print(f"AGENT DISPATCHED: Room={ctx.room.name}")
    
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(voice="shimmer"),
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
        instructions="Greet the user and begin the assessment."
    )


if __name__ == "__main__":
    agents.cli.run_app(server)
