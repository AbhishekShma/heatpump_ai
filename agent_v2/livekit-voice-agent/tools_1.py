# import logging
# from livekit.agents import function_tool, RunContext, get_job_context, ToolError
# import json
# import os
# import smtplib
# from email.mime.multipart import MIMEMultipart  
# from email.mime.text import MIMEText
# from typing import Optional
# from pathlib import Path
# import asyncio

# # @function_tool()
# # async def unblock_user(context: RunContext, username: str) -> str:
# #     """
# #     Unblock users so they can log in again.
# #     """
# #     try:
# #         # Get path to blockusers.txt
# #         THIS_DIR = Path(__file__).parent
# #         block_file = THIS_DIR / "generic_corporate_app" / "public" / "blockusers.txt"
        
# #         if not block_file.exists():
# #             logging.error(f"Block file not found at {block_file}")
# #             return "Unblock failed: blockusers.txt file not found"
            
# #         # Clear the file contents
# #         block_file.write_text("")
        
# #         logging.info("Successfully cleared blockusers.txt")
        
# #         room = get_job_context().room
# #         participant_identity = next(iter(room.remote_participants))
        
# #         try:
# #             # Add 3 second delay
# #             await asyncio.sleep(3)
# #             response = await room.local_participant.perform_rpc(
# #                 destination_identity=participant_identity,
# #                 method="client.showNotification",
# #                 payload=json.dumps({
# #                     "type": "unblock_user",
# #                     "username": username
# #                 }),
# #                 response_timeout=30.0  # Increased timeout to 30 seconds
# #             )
# #             logging.info(f"unblock_user response: {response}")
# #             return f"User {username} has been unblocked successfully and the response is: {response}"
# #         except Exception as rpc_error:
# #             logging.error(f"RPC error: {rpc_error}")
# #             # Still return success if file was cleared but RPC failed
# #             return f"User {username} has been unblocked, but notification failed: {str(rpc_error)}"
 
# #     except Exception as e:
# #         logging.error(f"Error clearing block file: {e}")
# #         raise ToolError("Unable to use tool unblock_user at this time.")

# # @function_tool()    
# # async def send_email(
# #     context: RunContext,  # type: ignore
# #     to_email: str,
# #     subject: str,
# #     message: str,
# #     cc_email: Optional[str] = None
# # ) -> str:
# #     """
# #     Send an email through Gmail.
    
# #     Args:
# #         to_email: Recipient email address
# #         subject: Email subject line
# #         message: Email body content
# #         cc_email: Optional CC email address
# #     """
# #     try:
# #         # Gmail SMTP configuration
# #         smtp_server = "smtp.gmail.com"
# #         smtp_port = 587
        
# #         # Get credentials from environment variables
# #         gmail_user = os.getenv("GMAIL_USER")
# #         gmail_password = os.getenv("GMAIL_APP_PASSWORD")  # Use App Password, not regular password
        
# #         if not gmail_user or not gmail_password:
# #             logging.error("Gmail credentials not found in environment variables")
# #             return "Email sending failed: Gmail credentials not configured."
        
# #         # Create message
# #         msg = MIMEMultipart()
# #         msg['From'] = gmail_user
# #         msg['To'] = to_email
# #         msg['Subject'] = subject
        
# #         # Add CC if provided
# #         recipients = [to_email]
# #         if cc_email:
# #             msg['Cc'] = cc_email
# #             recipients.append(cc_email)
        
# #         # Attach message body
# #         msg.attach(MIMEText(message, 'plain'))
        
# #         # Connect to Gmail SMTP server
# #         server = smtplib.SMTP(smtp_server, smtp_port)
# #         server.starttls()  # Enable TLS encryption
# #         server.login(gmail_user, gmail_password)
        
# #         # Send email
# #         text = msg.as_string()
# #         server.sendmail(gmail_user, recipients, text)
# #         server.quit()
        
# #         logging.info(f"Email sent successfully to {to_email}")

# #         room = get_job_context().room
# #         participant_identity = next(iter(room.remote_participants))

# #         try:
# #             # Add 3 second delay
# #             await asyncio.sleep(3)
# #             response = await room.local_participant.perform_rpc(
# #                 destination_identity=participant_identity,
# #                 method="client.showNotification",
# #                 payload=json.dumps({
# #                     "type": "send_email",
# #                     "email_address": to_email
# #                 }),
# #                 response_timeout=30.0  # Increased timeout to 30 seconds
# #             )
# #             logging.info(f"unblock_user response: {response}")
# #             return f"The email sent and the notification has been shown as well with response: {response}"
# #         except Exception as rpc_error:
# #             logging.error(f"RPC error: {rpc_error}")
# #             # Still return success if file was cleared but RPC failed
# #             return f"The notification to client was unsuccessful: {str(rpc_error)}"
        
# #     except smtplib.SMTPAuthenticationError:
# #         logging.error("Gmail authentication failed")
# #         return "Email sending failed: Authentication error. Please check your Gmail credentials."
# #     except smtplib.SMTPException as e:
# #         logging.error(f"SMTP error occurred: {e}")
# #         return f"Email sending failed: SMTP error - {str(e)}"
# #     except Exception as e:
# #         logging.error(f"Error sending email: {e}")
# #         return f"An error occurred while sending email: {str(e)}"
# FUNCTION_SCHEMA = {
#     "name": "run_heating_langgraph",
#     "description": "Start heating assessment. heating_data_json is a JSON string containing telemetry.",
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "heating_data_json": {"type": "string"}
#         },
#         "required": ["heating_data_json"],
#         "additionalProperties": False
#     }
# }

# @function_tool()
# async def run_heating_langgraph(
#     context: RunContext,  # type: ignore
#     heating_data: dict
# ) -> str:
#     """
#     Starts the heating assessment LangGraph in the background and returns immediately.
#     Use this tool when you want to begin processing heating_data without waiting for
#     the result. The tool will reply right away so the conversation can continue, and
#     the actual graph output will be delivered later as a separate tool-result message.
#     """
#     import asyncio
#     import json

#     async def background_job():
#         # --- REPLACE THIS with your real LangGraph call ---
#         await asyncio.sleep(2)  # simulate work
#         result = {
#             "graph": "heating_assessment_graph",
#             "output": "dummy result",
#             "input": heating_data
#         }

#         # <<< THE ONLY EXTRA LINE YOU NEED >>>
#         await context.session.send_tool_output("run_heating_langgraph", json.dumps(result))

#     # run in background and return immediately
#     asyncio.create_task(background_job())

#     return "Heating assessment started."

# # @function_tool()
# # async def run_heating_langgraph(
# #     context: RunContext,  # type: ignore
# #     heating_data: dict
# # ) -> str:
# #     """
# #     Call the heating assessment graph and return its result directly to the LLM.
# #     Replace the dummy graph call with your real LangGraph execution.
# #     """
# #     import json
# #     import asyncio

# #     # <<< REPLACE THIS with your real graph call
# #     await asyncio.sleep(1)  # simulate processing
# #     result = {
# #         "graph": "heating_assessment_graph",
# #         "input": heating_data,
# #         "output": "dummy result"
# #     }

# #     return json.dumps(result)


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

###########################Langgraph tool v1#################################################

@function_tool()
async def run_heating_langgraph(
    context: RunContext,
    duration: float = 5.0,
) -> str:
    """
    Run the heating assessment graph in the background.

    This tool is called only after the full interview is completed, all
    homeowner details have been gathered, the final summary has been created,
    and the user has verified its accuracy.

    The tool starts an asynchronous process that performs the heating
    feasibility calculation using the collected inputs. It returns immediately,
    allowing the agent to continue talking or listening while the graph runs.

    Arguments:
        duration: Temporary placeholder. The real implementation will receive
        the structured heating assessment summary and pass it into the LangGraph
        workflow. For now this argument simply controls how long the background
        task sleeps.

    Behavior:
        - The agent must call this tool exactly once, only after the completed
          and confirmed summary is generated.
        - The tool launches the background job and does not block the
          conversation.
        - The current version simulates the graph execution with
          asyncio.sleep(duration).

    Returns:
        A confirmation message indicating that the heating assessment has begun
        running in the background.
    """

    async def _worker():
        await asyncio.sleep(30)  # <-- replace with actual graph execution
        temp_return_val ="[background] Heating assessment graph finished, a good system is PJ30000"
        print(temp_return_val)


    asyncio.create_task(_worker())

    return "Heating assessment started in the background."

# ###########################Testing the Graph tool##########################################
# test_run_heating_graph.py
import asyncio
from datetime import datetime
# from run_heating_graph_tool import run_heating_langgraph

async def main():
    print("TEST START:", datetime.utcnow().isoformat(), "Z")

    # Call the tool. It should return immediately while the background worker runs.
    resp = await run_heating_langgraph(None, duration=3.0)
    print("Tool returned immediately:", resp)

    # Simulate agent continuing the conversation (do other async work).
    # We'll print a few messages while the background task sleeps.
    for i in range(3):
        print(f"Agent doing other work... step {i+1}")
        await asyncio.sleep(0.8)  # simulate handling other messages

    # Wait a bit longer than the background duration to ensure background finished.
    await asyncio.sleep(1.0)
    print("TEST END:", datetime.utcnow().isoformat(), "Z")

if __name__ == "__main__":
    asyncio.run(main())
####################################################################################################

####################### Run Heating Langgraph v2###################################################
# import asyncio
# import json
# import logging
# from typing import Any

# logger = logging.getLogger(__name__)

# @function_tool()
# async def run_heating_langgraph(
#     context: RunContext,
#     duration: float = 5.0,
# ) -> str:
#     """
#     Run the heating assessment graph in the background.

#     This tool is called only after the full interview is completed, all
#     homeowner details have been gathered, the final summary has been created,
#     and the user has verified its accuracy.

#     The tool starts an asynchronous process that performs the heating
#     feasibility calculation using the collected inputs. It returns immediately,
#     allowing the agent to continue talking or listening while the graph runs.

#     Note: this implementation triggers an LLM "thinking" turn (model-initiated)
#     when the graph finishes by calling `context.session.generate_reply(...)`.
#     """

#     async def _worker():
#         try:
#             # === REPLACE THIS with your real graph execution ===
#             # Simulate graph work; replace with: result = await run_graph_and_return_structured_result(...)
#             # await asyncio.sleep(duration)
#             await asyncio.sleep(5)
#             result: dict[str, Any] = {
#                 "status": "done",
#                 "recommendation": "PJ30000",
#                 "confidence": 0.93,
#                 # add any other structured fields your graph returns
#             }
#             # ==================================================
#         except Exception as exc:
#             logger.exception("Heating graph worker failed")

#             # If session still exists, ask the model to produce a failure reply so the agent notifies the user.
#             try:
#                 if not getattr(context.session, "closed", False):
#                     await context.session.generate_reply(
#                         "[background] Heating assessment failed while running the graph. "
#                         f"Error: {str(exc)}"
#                     )
#                 else:
#                     # session closed: persist failure so it can be surfaced later
#                     # IMPLEMENT persist_result_for_room(room_name, data) in your codebase
#                     try:
#                         await persist_result_for_room(
#                             getattr(context, "room_name", "unknown"),
#                             {"status": "failed", "error": str(exc)},
#                         )
#                     except Exception:
#                         logger.exception("Failed to persist failure after session closed")
#             except Exception:
#                 logger.exception("Failed while notifying model of worker failure")
#             return

#         # If session/room is closed, persist result instead of trying to kick the model
#         if getattr(context.session, "closed", False):
#             try:
#                 await persist_result_for_room(
#                     getattr(context, "room_name", "unknown"),
#                     {"status": "done", "result": result},
#                 )
#             except Exception:
#                 logger.exception("Failed to persist heating graph result after session closed")
#             return

#         # Build a compact payload and a short instruction so the LLM treats this as tool output.
#         payload_text = "### TOOL_RESULT HEATING_GRAPH\n" + json.dumps(result, ensure_ascii=False)

#         # Instruction must be short and prescriptive to reduce hallucination.
#         instruction = (
#             "You are the agent. The following is a structured tool result from the heating assessment. "
#             "Produce a concise, user-facing summary (one or two sentences) and a single recommended system. "
#             "Do NOT invent additional measurements; only use the provided JSON."
#         )

#         try:
#             # This triggers a model-initiated turn: the model will receive the payload and generate the next agent reply.
#             # await context.session.generate_reply(instruction + "\n\n" + payload_text)
            
#             await context.session.generate_reply(instructions=instruction + "\n\n" + payload_text) # prefer this: give the model an instruction + payload
#         except Exception as exc:
#             logger.exception("Failed to trigger generate_reply() from worker")
#             # Fallback: attempt to send a minimal notice (bypasses LLM) so participants know something happened.
#             try:
#                 if not getattr(context.session, "closed", False):
#                     await context.session.say(
#                         "[background] Heating assessment completed but automatic agent reply failed."
#                     )
#                 else:
#                     await persist_result_for_room(
#                         getattr(context, "room_name", "unknown"),
#                         {"status": "done", "result": result, "notify_failure": str(exc)},
#                     )
#             except Exception:
#                 logger.exception("Fallback notification also failed")

#     # start background worker and return immediately
#     try:
#         asyncio.create_task(_worker())
#     except Exception:
#         logger.exception("Failed to spawn heating graph worker")

#     return "Heating assessment started in the background."

##############################################################################################
# ###########################Testing the Graph tool v2##########################################

# # test_run_heating_graph.py
# import asyncio
# from datetime import datetime
# # from tools import run_heating_langgraph   # import your tool here

# # --- DummySession matching LiveKit's generate_reply signature ---
# class DummySession:
#     def __init__(self):
#         self.closed = False

#     # Accept keyword-only signature similar to LiveKit:
#     async def generate_reply(
#         self,
#         *,
#         user_input=None,
#         instructions=None,
#         tool_choice=None,
#         allow_interruptions=None,
#         chat_ctx=None,
#     ):
#         print("DUMMY SESSION: generate_reply called")
#         if user_input is not None:
#             print(" user_input:", user_input)
#         if instructions is not None:
#             print(" instructions:", instructions)
#         if tool_choice is not None:
#             print(" tool_choice:", tool_choice)
#         if allow_interruptions is not None:
#             print(" allow_interruptions:", allow_interruptions)
#         if chat_ctx is not None:
#             print(" chat_ctx:", chat_ctx)

#         # simulate returning a SpeechHandle-like object (not required for this test)
#         class DummyHandle:
#             def __init__(self):
#                 self.id = "dummy-speech-handle"
#         return DummyHandle()

#     async def say(self, text: str):
#         print("DUMMY SESSION: say called with:")
#         print(text)


# # Minimal mock context
# class DummyContext:
#     def __init__(self, room_name="test-room"):
#         self.session = DummySession()
#         self.room_name = room_name


# async def main():
#     print("TEST START:", datetime.utcnow().isoformat(), "Z")

#     ctx = DummyContext()

#     # Call the tool with the mock context. It should return immediately while background worker runs.
#     # Make sure to import your run_heating_langgraph from tools.py above.
#     resp = await run_heating_langgraph(ctx, duration=3.0)
#     print("Tool returned immediately:", resp)

#     # Simulate agent continuing the conversation (do other async work).
#     for i in range(6):
#         print(f"Agent doing other work... step {i+1}")
#         await asyncio.sleep(0.6)

#     # Wait a little longer to let background worker finish
#     await asyncio.sleep(2.0)
#     print("TEST END:", datetime.utcnow().isoformat(), "Z")


# if __name__ == "__main__":
#     asyncio.run(main())
####################################################################################################

####################### Run Heating Langgraph v3###################################################
# import asyncio
# import json
# import logging
# from typing import Any

# logger = logging.getLogger(__name__)

# @function_tool()
# async def run_heating_langgraph(context: RunContext, duration: float = 5.0) -> str:
#     async def _worker():
#         # -- defensive grabs
#         try:
#             job_id = getattr(context, "job_id", None)
#             room_name = getattr(context, "room_name", "unknown")
#             session = getattr(context, "session", None) if context is not None else None
#         except Exception as e:
#             logger.exception("Failed to read context attributes at worker start")
#             session = None
#             job_id = None
#             room_name = "unknown"

#         logger.info("heating worker started (job=%s room=%s)", job_id, room_name)

#         # Optional: dedupe guard (no-op: replace with persistent check)
#         try:
#             if job_id is not None:
#                 # Implement real dedupe: return early if already notified
#                 already_done = False  # <- query your DB/cache
#                 if already_done:
#                     logger.info("Job %s already completed; exiting worker", job_id)
#                     return
#         except Exception:
#             logger.exception("Error checking dedupe for job %s", job_id)

#         # Run the real graph (replace sleep)
#         try:
#             logger.debug("Running heating graph for job=%s", job_id)
#             # REPLACE: result = await run_graph_and_return_structured_result(...)
#             await asyncio.sleep(duration)
#             result: dict[str, Any] = {"status": "done", "recommendation": "PJ30000", "confidence": 0.93}
#             logger.debug("Graph finished for job=%s result=%s", job_id, result)
#         except Exception as exc:
#             logger.exception("Graph execution failed for job=%s", job_id)
#             # notify model if possible
#             if session is not None and not getattr(session, "closed", False):
#                 try:
#                     await session.generate_reply(instructions=f"[background] Heating assessment failed: {exc}")
#                 except Exception:
#                     logger.exception("generate_reply failed while reporting graph failure for job=%s", job_id)
#                     try:
#                         await session.say(f"[background] Heating assessment failed: {exc}")
#                     except Exception:
#                         logger.exception("say() fallback failed while reporting graph failure for job=%s", job_id)
#             else:
#                 # persist failure
#                 try:
#                     await persist_result_for_room(room_name, {"status": "failed", "error": str(exc), "job_id": job_id})
#                 except Exception:
#                     logger.exception("Failed to persist failure for job=%s", job_id)
#             return

#         # If session missing or closed, persist and exit
#         if session is None or getattr(session, "closed", False):
#             logger.info("Session missing/closed for job=%s; persisting result", job_id)
#             try:
#                 await persist_result_for_room(room_name, {"status": "done", "result": result, "job_id": job_id})
#             except Exception:
#                 logger.exception("Failed to persist result for job=%s", job_id)
#             return

#         # Optional: check activity/runtime state to avoid RuntimeError
#         try:
#             activity = getattr(session, "_activity", None)
#             scheduling_paused = getattr(activity, "scheduling_paused", None) if activity is not None else None
#             logger.debug("Session/activity state for job=%s: activity=%s scheduling_paused=%s", job_id, bool(activity), scheduling_paused)
#         except Exception:
#             logger.exception("Error reading session.activity for job=%s", job_id)

#         # Build payload and instruction
#         payload_text = "### TOOL_RESULT HEATING_GRAPH\n" + json.dumps(result, ensure_ascii=False)
#         instruction = (
#             "You are the agent. The following is a structured tool result from the heating assessment. "
#             "Produce a concise, user-facing summary and a single recommended system. "
#             "Do NOT invent additional measurements; only use the provided JSON."
#         )
#         combined = instruction + "\n\n" + payload_text

#         # Attempt to trigger generate_reply and log everything
#         try:
#             logger.info("Calling generate_reply for job=%s", job_id)
#             await session.generate_reply(instructions=combined)
#             logger.info("generate_reply succeeded for job=%s", job_id)
#             # Mark completed in DB so we don't notify twice (implement real persist)
#             try:
#                 await persist_result_for_room(room_name, {"status": "done", "notified": True, "job_id": job_id})
#             except Exception:
#                 logger.exception("Failed to persist notification flag for job=%s", job_id)
#             return
#         except Exception as exc:
#             logger.exception("generate_reply() failed for job=%s; will try fallbacks", job_id)

#         # Fallback: try user_input= then positional then say()
#         try:
#             await session.generate_reply(user_input=combined)
#             logger.info("generate_reply(user_input=...) succeeded for job=%s", job_id)
#             return
#         except Exception:
#             logger.exception("generate_reply(user_input=...) failed for job=%s", job_id)

#         try:
#             await session.generate_reply(combined)
#             logger.info("generate_reply(positional) succeeded for job=%s", job_id)
#             return
#         except Exception:
#             logger.exception("generate_reply(positional) failed for job=%s", job_id)

#         # Final fallback: send a say() so participants are notified
#         try:
#             logger.warning("All generate_reply variants failed for job=%s; falling back to say()", job_id)
#             await session.say("[background] Heating assessment completed (agent reply failed to start).")
#             # persist as notified=false
#             try:
#                 await persist_result_for_room(room_name, {"status": "done", "notified": False, "job_id": job_id})
#             except Exception:
#                 logger.exception("Failed to persist fallback notify for job=%s", job_id)
#         except Exception:
#             logger.exception("Fallback say() also failed for job=%s; persisting result", job_id)
#             try:
#                 await persist_result_for_room(room_name, {"status": "done", "result": result, "notify_failure": True, "job_id": job_id})
#             except Exception:
#                 logger.exception("Persist fallback also failed for job=%s", job_id)

#     # spawn background task
#     try:
#         asyncio.create_task(_worker())
#     except Exception:
#         logger.exception("Failed to spawn heating graph worker")
#     return "Heating assessment started in the background."
##############################################################################################






# ###########################Testing the Graph tool v3##########################################

# # ---------- BEGIN TEST HARNESS (drop into tools.py after your tool) ----------
# import asyncio
# import json
# import logging
# from datetime import datetime
# from pathlib import Path
# from typing import Any

# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)

# # --- Simple persistence for tests: in-memory + JSON file
# _PERSIST_STORE: dict[str, Any] = {}
# _PERSIST_FILE = Path("heating_results.json")

# async def persist_result_for_room(room_name: str, data: dict[str, Any]) -> None:
#     """
#     Test stub that persists a small record in memory and appends to a JSON file.
#     Replace this with real DB/cache in production.
#     """
#     key = f"{room_name}:{data.get('job_id', 'no-job')}"
#     _PERSIST_STORE[key] = data
#     try:
#         current = []
#         if _PERSIST_FILE.exists():
#             try:
#                 current = json.loads(_PERSIST_FILE.read_text())
#             except Exception:
#                 current = []
#         current.append({"room": room_name, **data})
#         _PERSIST_FILE.write_text(json.dumps(current, ensure_ascii=False, indent=2))
#     except Exception:
#         logger.exception("persist_result_for_room file write failed (test stub)")

# # --- DummySession matching LiveKit's generate_reply signature ---
# class DummySession:
#     def __init__(self):
#         self.closed = False

#     async def generate_reply(
#         self,
#         *,
#         user_input=None,
#         instructions=None,
#         tool_choice=None,
#         allow_interruptions=None,
#         chat_ctx=None,
#     ):
#         print("DUMMY SESSION: generate_reply called")
#         if user_input is not None:
#             print(" user_input:", user_input)
#         if instructions is not None:
#             print(" instructions:", instructions)
#         if tool_choice is not None:
#             print(" tool_choice:", tool_choice)
#         if allow_interruptions is not None:
#             print(" allow_interruptions:", allow_interruptions)
#         if chat_ctx is not None:
#             print(" chat_ctx:", chat_ctx)

#         # return a dummy handle object similar to SpeechHandle for completeness
#         class DummyHandle:
#             def __init__(self):
#                 self.id = "dummy-speech-handle"
#         return DummyHandle()

#     async def say(self, text: str):
#         print("DUMMY SESSION: say called with:")
#         print(text)

# # --- DummyContext used to call your tool in tests ---
# class DummyContext:
#     def __init__(self, room_name="test-room", job_id="job-test-1"):
#         self.session = DummySession()
#         self.room_name = room_name
#         self.job_id = job_id

# # --- Test runner that calls your run_heating_langgraph tool ---
# async def _test_run(duration: float = 3.0):
#     print("TEST START:", datetime.utcnow().isoformat(), "Z")
#     ctx = DummyContext(room_name="unit-test-room", job_id="job-test-1")

#     # If run_heating_langgraph is defined in this file, call it directly.
#     # If it's imported from elsewhere, make sure the name points to the correct function.
#     try:
#         resp = await run_heating_langgraph(ctx, duration=duration)
#     except Exception as exc:
#         logger.exception("Tool call failed in test harness: %s", exc)
#         return

#     print("Tool returned immediately:", resp)

#     # Simulate agent doing other work while the background task runs
#     for i in range(6):
#         print(f"Agent doing other work... step {i+1}")
#         await asyncio.sleep(0.6)

#     # Wait extra time to let background worker finish
#     await asyncio.sleep(duration + 1.0)
#     print("TEST END:", datetime.utcnow().isoformat(), "Z")

# if __name__ == "__main__":
#     # Run the test harness when this file is executed directly.
#     try:
#         asyncio.run(_test_run(duration=3.0))
#     except KeyboardInterrupt:
#         print("Test interrupted by user")
# # ---------- END TEST HARNESS ----------

####################################################################################################