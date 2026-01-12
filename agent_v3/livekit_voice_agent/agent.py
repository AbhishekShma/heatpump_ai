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

from tools import get_current_time, json_extraction_tool
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
            tools=[get_current_time, json_extraction_tool],
        )


server = AgentServer()


@server.rtc_session(agent_name="assistant")
async def my_agent(ctx: agents.JobContext):
    """
    Main agent session handler.
    Uses OpenAI Realtime API which includes STT, LLM, TTS, and turn detection.
    """
    print(f"AGENT DISPATCHED: Room={ctx.room.name}")
    
    session = AgentSession(
        # OpenAI Realtime API includes built-in turn detection, STT, LLM, and TTS
        llm=openai.realtime.RealtimeModel(
            voice="shimmer"  # Options: alloy, echo, fable, onyx, nova, shimmer
        ),
        # Turn detection is built into OpenAI Realtime API
        turn_detection=None,
    )

    ##############PRINT STT TEXT (User Transcripts) ##########################
    def on_user_input_transcribed(event):
        """Handle user transcription events"""
        # Only print when transcript is not empty and is final
        if hasattr(event, 'transcript') and event.transcript and event.is_final:
            print("🎤 USER:", event.transcript)
    
    session.on("user_input_transcribed", on_user_input_transcribed)

    ##############PRINT AGENT TRANSCRIPTS (Agent Speech) ##########################
    # Listen for agent speech committed event (when agent finishes speaking)
    def on_agent_speech_committed(event):
        """Handle agent speech committed events - this is the correct event"""
        if hasattr(event, 'transcript') and event.transcript:
            print("🤖 AGENT:", event.transcript)
        elif hasattr(event, 'text') and event.text:
            print("🤖 AGENT:", event.text)
        else:
            print("🤖 AGENT Speech Committed Event:", event)
            print("🤖 Event attributes:", [x for x in dir(event) if not x.startswith('_')])
    
    session.on("agent_speech_committed", on_agent_speech_committed)
    
    # Also try alternative event names
    def on_agent_output_transcribed(event):
        """Alternative handler for agent transcription"""
        if hasattr(event, 'transcript') and event.transcript:
            print("🤖 AGENT (output_transcribed):", event.transcript)
        else:
            print("🤖 Agent Output Transcribed Event:", event)
    
    session.on("agent_output_transcribed", on_agent_output_transcribed)
    
    # Listen for conversation items being added (includes agent responses)
    def on_conversation_item_added(event):
        """Handle conversation items - includes agent responses"""
        if hasattr(event, 'item'):
            item = event.item
            # Check if it's an agent/assistant item
            if hasattr(item, 'role') and item.role in ['assistant', 'agent']:
                if hasattr(item, 'content') and item.content:
                    print("🤖 AGENT (conversation):", item.content)
                elif hasattr(item, 'text') and item.text:
                    print("🤖 AGENT (conversation):", item.text)
            else:
                print("📝 Conversation Item:", item)
    
    session.on("conversation_item_added", on_conversation_item_added)
    
    # Listen to room transcript events and filter by participant
    def on_room_transcript(event):
        """Handle room-level transcript events - filter for agent"""
        print("📝 ROOM TRANSCRIPT EVENT RECEIVED")
        # Check if this is from the agent participant
        if hasattr(event, 'participant') and event.participant:
            participant = event.participant
            if hasattr(participant, 'identity'):
                identity = participant.identity.lower()
                if 'agent' in identity:
                    if hasattr(event, 'text') and event.text:
                        print("🤖 AGENT (room):", event.text)
                    elif hasattr(event, 'transcript') and event.transcript:
                        print("🤖 AGENT (room):", event.transcript)
        elif hasattr(event, 'text') and event.text:
            # Print all room transcripts for debugging
            print("📝 ROOM TRANSCRIPT:", event.text)
        else:
            print("📝 Room Transcript Event:", event)
    
    ctx.room.on("transcript_received", on_room_transcript)

    ##############PRINT AGENT RESPONSE (What agent says) ##########################
    # With Realtime API, the agent's speech is generated from LLM output
    # This is what the agent actually says
    def on_assistant_response(event):
        """Handle assistant response - this is what the agent says"""
        if hasattr(event, 'type') and event.type == "output_text":
            print("🤖 AGENT:", event.text)
        elif hasattr(event, 'text') and event.text:
            print("🤖 AGENT:", event.text)
        elif hasattr(event, 'content') and event.content:
            print("🤖 AGENT:", event.content)

    session.on("assistant_response", on_assistant_response)

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
        # instructions=f"Greet the user and begin the assessment as per {AGENT_INSTRUCTIONS}."
        instructions=f"Convert what I say in hindi into english."
    )


if __name__ == "__main__":
    agents.cli.run_app(server)

