from dotenv import load_dotenv

from livekit import agents, rtc
from livekit.agents import AgentServer,AgentSession, Agent, room_io
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from tools import get_current_time,run_heating_langgraph
from prompts import AGENT_INSTRUCTIONS

load_dotenv(".env")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTIONS,
            # tools=[get_current_time,run_heating_langgraph],
            tools=[get_current_time],
        )
server = AgentServer()

@server.rtc_session(agent_name="assistant")
async def my_agent(ctx: agents.JobContext):
    session = AgentSession(
    stt="assemblyai/universal-streaming:en",
    # stt=None,
    llm="openai/gpt-4.1-mini",
    tts="cartesia/sonic-3:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
    # tts=None,
    turn_detection=None,
)
    ##############PRINT STT TEXT ##########################

    def on_transcription(event):
        # event is a UserInputTranscribedEvent
        text = event.transcript
        print("======================STT==========================>:", text)

    session.on("user_input_transcribed", on_transcription)
    #########################################################

    ################### PRINT TTS TEXT (LLM reply before speech)#########################
    def on_conversation_item_added(event):
        if event.item.role == "assistant":
            for content in event.item.content:
                if isinstance(content, str):
                    print("====================TTS Output Text==========================>:", content)
                else:
                    # content can be AudioContent, ImageContent, or objects with .text/.transcript
                    text = getattr(content, "text", None) or getattr(content, "transcript", None)
                    if text:
                        print("====================TTS Output Text==========================>:", text)

    session.on("conversation_item_added", on_conversation_item_added)
   ########################################################################     
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony() if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP else noise_cancellation.BVC(),
            ),
        ),
    )

    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )


if __name__ == "__main__":
    agents.cli.run_app(server)