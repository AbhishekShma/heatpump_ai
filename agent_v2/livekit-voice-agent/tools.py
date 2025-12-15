#####################################Date time Tool v1##################################
from datetime import datetime
from livekit.agents import function_tool, RunContext
import asyncio
@function_tool()
async def get_current_time(
    context: RunContext,  # LiveKit provides this automatically
) -> str:
    """
    Returns the current UTC time as an ISO8601 string.
    """
    now = datetime.utcnow()
    return now.isoformat() + "Z"


# import asyncio
# # from time_tool import get_current_time

# async def main():
#     result = await get_current_time(None)  # context not needed for this tool
#     print("Tool returned:", result)

# if __name__ == "__main__":
#     asyncio.run(main())
############################################################################################




###########################Langgraph tool v1#################################################
# import logging


# @function_tool()
# async def run_heating_langgraph(
#     context: RunContext,
#     duration: float = 5.0,
# ) -> str:
#     """
#     Launch background heating assessment and inject the result into the AgentSession
#     as an instruction (so it's not treated as user input).
#     """
#     async def _worker():
#         # simulate graph execution (replace with real LangGraph call)
#         await asyncio.sleep(duration)
#         temp_return_val = "Heating assessment graph finished, a good system is PJ30000"

#         # Build an instruction that injects the result and tells the LLM what to do with it.
#         # Keep it explicit and concise so the LLM knows to incorporate the data into the
#         # agent's reasoning & next reply rather than treating it as a user's utterance.
#         instruction_text = (
#             "Background process completed. Inject the following assessment result into the "
#             "current conversation context as system-provided data (not user input). "
#             "Then update the homeowner summary and recommend next steps.\n\n"
#             f"Assessment result:\n{temp_return_val}\n\n"
#             "Reply with: (1) short confirmation you received the data, (2) any changes to the "
#             "final recommendation, and (3) proposed next steps for the homeowner."
#         )

#         try:
#             # Inject as instructions (LLM will treat it as guidance/system instruction)
#             # Await the handle if you want to wait for the speech generation to start/complete.
#             print(f"=========================>{bool(context)}")
#             logging.getLogger(__name__).info("Worker context is %s", bool(context))
#             logging.getLogger(__name__).info(
#                 "Worker context.session is %s",
#                 bool(getattr(context, "session", None))
#             )
#             await context.session.generate_reply(
#                 instructions=instruction_text,
#                 # optional: specify tool_choice if you want a particular tool used for generation
#                 # tool_choice=llm.ToolChoice.OPENAI_CHAT, 
#                 # optional: pass ChatContext if you have structured metadata to attach
#                 # chat_ctx=my_chat_ctx,
#                 allow_interruptions=False,  # if you want the user to be able to interrupt speech
#             )
#         except Exception as e:
#             # log or handle error — keep the background job resilient
#             print("failed to inject background result into session:", e)
#             raise

#     # fire-and-forget background worker (keeps current behavior)
#     asyncio.create_task(_worker())

#     return "Heating assessment started in the background."

# ###########################Testing the Graph tool##########################################
# # test_run_heating_graph.py
# import asyncio
# from datetime import datetime
# # import your tool function (adjust import path as needed)
# # from run_heating_graph_tool import run_heating_langgraph
# from tools import run_heating_langgraph  # <- update to your actual module

# class DummySpeechHandle:
#     def __init__(self, text):
#         self.text = text

# class DummySession:
#     async def generate_reply(
#         self,
#         *,
#         user_input=None,
#         instructions=None,
#         tool_choice=None,
#         allow_interruptions=None,
#         chat_ctx=None,
#     ):
#         # This mocks the AgentSession.generate_reply behaviour sufficiently for testing.
#         # Print so we can see the injection in test output.
#         print("DummySession.generate_reply() called.")
#         if instructions is not None:
#             print("instructions passed to generate_reply:")
#             print(instructions)
#         elif user_input is not None:
#             print("user_input passed to generate_reply:")
#             print(user_input)
#         else:
#             print("generate_reply called with no text")
#         # Return a fake handle (your real code expects a SpeechHandle-like return)
#         return DummySpeechHandle("fake-handle")

# class DummyContext:
#     def __init__(self):
#         self.session = DummySession()

# async def main():
#     print("TEST START:", datetime.utcnow().isoformat(), "Z")

#     # Provide a dummy context with a .session.generate_reply coroutine implementation.
#     ctx = DummyContext()

#     # Call the tool. It should return immediately while the background worker runs.
#     resp = await run_heating_langgraph(ctx, duration=3.0)
#     print("Tool returned immediately:", resp)

#     # Simulate agent continuing the conversation (do other async work).
#     for i in range(3):
#         print(f"Agent doing other work... step {i+1}")
#         await asyncio.sleep(0.8)

#     # Give enough time for the background task to finish.
#     await asyncio.sleep(2.0)
#     print("TEST END:", datetime.utcnow().isoformat(), "Z")

# if __name__ == "__main__":
#     asyncio.run(main())
####################################################################################################


#################### Langgraph tool v2 #####################################################
import asyncio
import logging
from typing import Any

# configure logger at module level (adjust handler/level in your app startup if needed)
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# keep your existing decorator import; here it's shown as-is
# from your_framework import function_tool, RunContext

@function_tool()
async def run_heating_langgraph(
    context: "RunContext",
    duration: float = 5.0,
) -> str:
    """
    Launch background heating assessment.

    - DOES NOT call the actual LangGraph here (per your request).
    - Provides robust error handling & logging around the spot where the graph call would occur.
    - Fires a background worker and returns immediately so the agent is freed.
    """

    async def _worker() -> None:
        try:
            logger.info("Background worker started for heating assessment.")

            # === PLACE FOR ACTUAL GRAPH CALL (DO NOT CALL NOW) ===
            # When you implement the real call later, place it here. Example (pseudo):
            # result = await call_langgraph(payload)
            # logger.info("LangGraph call returned result summary: %s", summarize(result))
            #
            # IMPORTANT: Do not call the graph now. The line above is intentionally commented/pseudocode.
            # ==================================================

            # Simulate internal work or timeout while graph runs (safe placeholder)
            await asyncio.sleep(duration)

            # If you want to record a short success log now (the long result will be stored elsewhere):
            logger.info("Heating assessment background task completed (simulated).")

        except asyncio.CancelledError:
            # Task was cancelled; log at INFO (not an error) unless you want otherwise.
            logger.info("Heating assessment background task was cancelled.")
            raise  # re-raise if you want upstream cancellation behavior retained

        except Exception as exc:
            # Catch-all so nothing silently disappears. Log full traceback.
            logger.exception("Failed while running heating assessment background task: %s", exc)
            # Optionally you can write the error into the AgentSession or a monitoring system:
            try:
                # Example: attach an instruction or log to the AgentSession if available
                # context.session.add_instruction(f"Heating assessment failed to start: {exc}")
                # The above is commented because your implementation details may differ.
                pass
            except Exception:
                # If logging to session fails, don't let that mask the original error
                logger.exception("Also failed when trying to attach error to AgentSession.")

    # Try scheduling the background worker; if scheduling itself fails, return an error message.
    try:
        task = asyncio.create_task(_worker())
        # Optional: add a callback to capture unhandled exceptions (defensive)
        def _on_done(t: asyncio.Task[Any]) -> None:
            try:
                exc = t.exception()
                if exc is not None:
                    logger.exception("Background task finished with exception: %s", exc)
            except asyncio.CancelledError:
                logger.info("Background task callback saw cancellation.")
            except Exception:
                logger.exception("Error while handling background task completion callback.")

        task.add_done_callback(_on_done)
    except Exception as schedule_exc:
        # If we fail to schedule the background task, log and return an error message so the agent isn't freed under false pretenses.
        logger.exception("Could not start heating assessment background task: %s", schedule_exc)
        return f"Failed to start heating assessment: {schedule_exc}"

    # If scheduling succeeded, free up the agent and inform the user that analysis started.
    return "Heating assessment started in the background."
#######################################################################################################################################

############## Testing langgraph tool ######################################
# test_run_heating_graph.py
import asyncio
import logging
from datetime import datetime

# Adjust the import path to wherever your tool is defined
from tools import run_heating_langgraph  


# -------------------------------------------------------------------
# Dummy context and session to satisfy the tool signature
# -------------------------------------------------------------------

class DummySession:
    """
    Your new tool does not call session.generate_reply(), so this is
    intentionally minimal. It's only here because the context needs it.
    """
    async def generate_reply(self, **kwargs):
        print("generate_reply called (should not happen in new tool).")
        return None


class DummyContext:
    def __init__(self):
        self.session = DummySession()


# -------------------------------------------------------------------
# Run the test
# -------------------------------------------------------------------

async def main():
    print("TEST START:", datetime.utcnow().isoformat(), "Z")

    # Enable logging visibility for demonstration
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s"
    )

    ctx = DummyContext()

    print("Calling run_heating_langgraph()...")
    resp = await run_heating_langgraph(ctx, duration=2.0)
    print("Tool return value:", resp)

    # Simulate independent agent work
    for i in range(3):
        print(f"Agent doing other work... step {i+1}")
        await asyncio.sleep(0.6)

    # Wait long enough for the background task to finish and log output
    print("Waiting for background worker to finish...")
    await asyncio.sleep(2.0)

    print("TEST END:", datetime.utcnow().isoformat(), "Z")


if __name__ == "__main__":
    asyncio.run(main())
######################################################################################