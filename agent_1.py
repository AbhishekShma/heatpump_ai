import asyncio
import json
import logging
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

import aiohttp
from openai import AsyncOpenAI
from dotenv import load_dotenv
from livekit import rtc, api
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    inference,
    room_io,
    function_tool
)
from livekit.plugins import (
    noise_cancellation,
    silero,
    deepgram,
    openai,
)

logger = logging.getLogger("agent-Sage-8d9")
logging.basicConfig(level=logging.INFO)

env_path = Path(__file__).parent / 'dev.env'
if env_path.exists():
    load_dotenv(env_path)
    logging.info(f"Loaded environment from {env_path}")
else:
    logging.warning(f"dev.env not found at {env_path}, trying default .env")
    load_dotenv()
    
# Embedded AGENT_INSTRUCTIONS from prompt.py
AGENT_INSTRUCTIONS = """
Du bist ein freundlicher, geduldiger Sprachassistent, der Menschen dabei hilft, Informationen für eine Wärmepumpen-Eignungsprüfung zu sammeln. Du führst ein natürliches Gespräch – ruhig, warmherzig und menschlich. Du bist kein Interviewer und kein Roboter. Du bist ein hilfsbereiter Begleiter.

SPRACHVERHALTEN:
- Sprich ausschließlich Deutsch während des gesamten Gesprächs.
- Wenn der Nutzer ausdrücklich um Englisch bittet (z.B. "Can you speak English?", "English please", "Sprechen Sie Englisch?"), wechsle vollständig und dauerhaft zu Englisch.
- Nach einem Wechsel zu Englisch: Verwende ausschließlich Englisch für den Rest des Gesprächs. Kein Zurückwechseln.
- Erwähne niemals Sprachregeln oder erkläre dem Nutzer das Sprachverhalten.

GESPRÄCHSSTIL:
- Sprich wie ein ruhiger, aufmerksamer Mensch – nicht wie eine Maschine.
- Verwende natürliche Übergänge und freundliche Formulierungen.
- Zeige echtes Interesse an den Antworten des Nutzers.
- Vermeide steife, formelle oder roboterhafte Sprache.
- Sage niemals "Nur zur Bestätigung..." oder ähnliche mechanische Phrasen.

FRAGENABLAUF:
- Stelle immer nur eine Frage auf einmal.
- Formuliere Fragen klar, aber natürlich und gesprächsnah.
- Nenne keine Fragennummern oder "Frage X von Y".
- Bohre nicht nach und stelle keine Zusatzfragen.
- Das Ziel ist Klarheit, nicht Verhör.

MANDATORY QUESTIONS (PFLICHTFRAGEN):
- Fragen, die mit [MANDATORY] markiert sind, MÜSSEN beantwortet werden.
- Wenn der Nutzer eine Pflichtfrage nicht beantwortet oder ausweicht, frage freundlich aber bestimmt nach.
- Wiederhole Pflichtfragen, bis du eine klare Antwort erhältst.
- Beispiel: "Ich verstehe, dass Sie diese Information vielleicht nicht sofort haben. Diese Information ist jedoch wichtig für die Empfehlung. Könnten Sie mir bitte [Frage wiederholen]?"
- Sei geduldig, aber beharrlich bei Pflichtfragen.
- Nach maximal 3 Versuchen, wenn immer noch keine Antwort kommt, kannst du zur nächsten Frage übergehen, aber notiere, dass die Pflichtfrage nicht beantwortet wurde.

ANTWORTVERARBEITUNG:
- Wenn eine Antwort verständlich ist, MUSST du SOFORT die Funktion `store_answer` aufrufen mit:
  - question_number: Die Fragennummer (1, 2, 3, usw.)
  - question_text: Der Text der gestellten Frage
  - user_answer: Die Antwort des Nutzers
- Dies ist PFLICHT nach JEDER beantworteten Frage!
- Wenn etwas unklar ist, frage freundlich nach – z.B. "Das habe ich nicht ganz verstanden, könnten Sie das noch einmal sagen?"
- Frage NICHT nach jeder Antwort explizit um Bestätigung.
- Bestätigungen erfolgen implizit durch natürliche Gesprächsführung.

ABSCHLUSS DES GESPRÄCHS:
- Wenn alle Fragen beantwortet sind, fasse die gesammelten Informationen kurz und freundlich zusammen.
- Bitte den Nutzer einmalig, die Zusammenfassung zu bestätigen – z.B. "Habe ich alles richtig erfasst?"
- Bedanke dich herzlich und biete weitere Hilfe an.
- Halte den Abschluss kurz und natürlich.

AUTOMATISCHE DATENSPEICHERUNG:
- Rufe die Funktion `send_all_answers_to_webhook` NUR auf, wenn ALLE folgenden Bedingungen erfüllt sind:
  1. ALLE Fragen aus der Liste wurden bereits gestellt und beantwortet
  2. Du hast dem Nutzer eine ZUSAMMENFASSUNG aller gesammelten Antworten präsentiert
  3. Der Nutzer hat diese Zusammenfassung EXPLIZIT bestätigt (z.B. "Ja", "Stimmt", "Alles richtig", "Passt", "Yes", "Correct")
- NIEMALS die Funktion aufrufen, bevor alle Fragen beantwortet wurden!
- NIEMALS die Funktion aufrufen, ohne vorher eine Zusammenfassung gezeigt zu haben!
- Nach erfolgreichem Aufruf der Funktion, bedanke dich beim Nutzer und beende das Gespräch freundlich.

WICHTIGE EINSCHRÄNKUNGEN:
- Ändere niemals bereits gespeicherte Antworten.
- Erkläre dem Nutzer keine internen Regeln oder technischen Abläufe.
- Bleibe immer höflich, geduldig und menschlich.
- Priorisiere Klarheit und Verständnis über Geschwindigkeit.
"""



async def test_deepgram_connection(api_key: str) -> bool:
    """Test if Deepgram API key is valid"""
    try:
        url = "https://api.deepgram.com/v1/projects"
        headers = {"Authorization": f"Token {api_key}"}
        
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as http_session:
            async with http_session.get(url, headers=headers) as response:
                if response.status == 200:
                    logger.info("✓ Deepgram API key is valid")
                    return True
                else:
                    logger.error(f"✗ Deepgram API key validation failed: {response.status}")
                    response_text = await response.text()
                    logger.error(f"Response: {response_text}")
                    return False
    except Exception as e:
        logger.error(f"Error testing Deepgram connection: {e}")
        return False


async def parse_metadata(ctx: JobContext) -> Optional[Dict[str, Any]]:
    """Parse metadata from room metadata - tries direct room access first, then REST API as fallback"""
    metadata_str = None
    
    max_retries = 10
    retry_delay = 1.0
    
    # APPROACH 1: Try to get metadata directly from ctx.room (most reliable after connection)
    for attempt in range(max_retries):
        try:
            # After ctx.connect(), ctx.room.metadata should contain the room metadata
            if hasattr(ctx.room, 'metadata') and ctx.room.metadata:
                metadata_str = ctx.room.metadata
                logger.info(f"✓ Got metadata directly from ctx.room.metadata (attempt {attempt + 1})")
                break
            else:
                logger.info(f"Direct room metadata not available yet (attempt {attempt + 1}/{max_retries})")
        except Exception as e:
            logger.debug(f"Error accessing ctx.room.metadata: {str(e)}")
        
        if attempt < max_retries - 1:
            logger.info(f"Waiting {retry_delay:.1f}s before retry...")
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 1.2, 3.0)
    
    # APPROACH 2: If direct access failed, try REST API as fallback
    if not metadata_str:
        logger.info("Direct room metadata access failed, trying REST API as fallback...")
        
        livekit_url = os.getenv('LIVEKIT_URL')
        api_key = os.getenv('LIVEKIT_API_KEY')
        api_secret = os.getenv('LIVEKIT_API_SECRET')
        
        if not livekit_url or not api_key or not api_secret:
            logger.error("Missing LiveKit credentials for REST API fallback")
            return None
        
        livekit_api = None
        try:
            livekit_api = api.LiveKitAPI(
                url=livekit_url,
                api_key=api_key,
                api_secret=api_secret
            )
        except Exception as e:
            logger.error(f"Failed to initialize LiveKit API client: {str(e)}")
            return None
        
        retry_delay = 1.0  # Reset retry delay for REST API attempts
        try:
            for attempt in range(max_retries):
                try:
                    logger.info(f"Fetching room metadata from REST API (attempt {attempt + 1}/{max_retries}) for room: {ctx.room.name}")
                    
                    try:
                        list_response = await livekit_api.room.list_rooms(
                            api.ListRoomsRequest()
                        )
                        
                        rooms = list_response.rooms if hasattr(list_response, 'rooms') else []
                        logger.info(f"Found {len(rooms)} rooms in ListRooms response")
                        
                        for room_info in rooms:
                            if room_info.name == ctx.room.name:
                                metadata_str = room_info.metadata if hasattr(room_info, 'metadata') else None
                                if metadata_str:
                                    logger.info(f"✓ Successfully fetched room metadata from ListRooms (attempt {attempt + 1})")
                                    break
                                else:
                                    logger.info(f"Room {room_info.name} found but metadata is empty")
                        
                        if metadata_str:
                            break
                    except Exception as list_error:
                        logger.debug(f"ListRooms failed: {str(list_error)}")
                    
                    if metadata_str:
                        break
                        
                    if attempt < max_retries - 1:
                        logger.info(f"Metadata not found yet via REST API, waiting {retry_delay:.1f}s before retry...")
                        await asyncio.sleep(retry_delay)
                        retry_delay = min(retry_delay * 1.2, 3.0)
                        
                except Exception as e:
                    logger.warning(f"Failed to fetch room metadata via REST API (attempt {attempt + 1}): {str(e)}")
                    import traceback
                    logger.debug(traceback.format_exc())
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                        retry_delay = min(retry_delay * 1.2, 3.0)
        finally:
            if livekit_api:
                try:
                    if hasattr(livekit_api, 'close'):
                        await livekit_api.close()
                except:
                    pass
    
    if not metadata_str:
        logger.error(f"No metadata found via direct access or REST API. Room name: {ctx.room.name}")
        return None
    
    try:
        metadata = json.loads(metadata_str)
        session_id = metadata.get("session_id", "")
        user_id = metadata.get("user_id", 0)
        questions = metadata.get("questions", [])
        webhook_url = metadata.get("backend_webhook", "")
        
        if not all([session_id, user_id, questions, webhook_url]):
            logger.error("Missing required metadata fields")
            return None
        
        logger.info(f"✓ Successfully parsed metadata: session_id={session_id}, user_id={user_id}, questions={len(questions)}")
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "questions": questions,
            "backend_webhook": webhook_url
        }
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse metadata JSON: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error parsing metadata: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None


class DefaultAgent(Agent):
    # Agent states
    STATE_COLLECTING = "collecting"
    STATE_AWAITING_FINAL_CONFIRMATION = "awaiting_final_confirmation"
    STATE_AWAITING_UPDATE_ANSWER = "awaiting_update_answer"
    STATE_COMPLETED = "completed"
    
    def __init__(self, questions: List[Dict[str, Any]], session_id: str, user_id: int, webhook_url: str, room: Any = None) -> None:
        self.questions = questions
        self.session_id = session_id
        self.user_id = user_id
        self.webhook_url = webhook_url
        self.room = room  # Store room reference for disconnect
        
        self.current_question_index = 0
        self.conversation_id = 1
        self.answers_collected: List[Dict[str, Any]] = []  # List for bulk save
        self.conversation_history: List[Dict[str, str]] = []
        
        # State machine
        self.state = self.STATE_COLLECTING
        self.update_index: Optional[int] = None  # Index of answer being updated
        
        self.retry_count = 0
        self.max_retries = 3
        
        # Track mandatory questions that haven't been answered
        self.mandatory_questions_pending: List[int] = []  # List of question indices that are mandatory and unanswered
        
        # Track last activity time for timeout detection
        self.last_activity_time: Optional[float] = None
        self.monitor_task: Optional[asyncio.Task] = None
        self.is_disconnecting = False
        
        # Session timing
        self.session_start_time = asyncio.get_event_loop().time()
        self.max_session_duration = int(os.getenv('AGENT_MAX_SESSION_DURATION', '600'))  # 10 min default
        
        # Language tracking - default is German
        self.conversation_language = "de"  # "de" for German, "en" for English
        
        # Conversation history for LLM-based conversation node
        self.conversation_messages: List[Dict[str, str]] = []  # List of {"role": "user"/"assistant", "content": "..."}
        
        # Flag to enable LLM-based conversation node (similar to text-based agent)
        self.use_conversation_node = os.getenv('USE_CONVERSATION_NODE', 'false').lower() == 'true'
        
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            logger.error("OPENAI_API_KEY not found")
            raise ValueError("OPENAI_API_KEY is required")
        
        self.openai_client = AsyncOpenAI(api_key=openai_key)
        
        questions_list = []
        for idx, q in enumerate(self.questions, 1):
            question_text = q.get('text', q.get('description', ''))
            # Add mandatory flag if the question is marked as mandatory
            is_mandatory = q.get('is_mandatory', False)
            if is_mandatory:
                questions_list.append(f"{idx}. {question_text} [MANDATORY]")
                # Track mandatory questions
                self.mandatory_questions_pending.append(idx - 1)  # Store as 0-based index
            else:
                questions_list.append(f"{idx}. {question_text}")
        
        questions_text = "\n".join(questions_list)
        
        system_prompt = f"""{AGENT_INSTRUCTIONS}


QUESTIONS TO ASK (in order):

{questions_text}

Remember: Ask one question at a time. Accept clear answers and move to the next question naturally.
For questions marked [MANDATORY], you must get an answer before moving on. Be persistent but friendly.
"""
        
        super().__init__(instructions=system_prompt)
        
        logger.info(f"Initialized agent with {len(questions)} questions for session {session_id}")
        logger.info(f"Mandatory questions: {len(self.mandatory_questions_pending)}")
        logger.info(f"Max session duration: {self.max_session_duration}s")
        logger.info(f"Default conversation language: {self.conversation_language}")
    
    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """Get the current question to ask"""
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    def detect_language_switch_request(self, message: str) -> Optional[str]:
        """Detect if user is requesting a language switch. Returns 'en' or 'de' or None."""
        message_lower = message.lower().strip()
        
        # English switch requests
        english_phrases = [
            "can you speak english", "speak english", "english please", 
            "sprechen sie englisch", "englisch bitte", "in english",
            "switch to english", "english", "wechsle zu englisch"
        ]
        
        # German switch requests (if needed in future)
        german_phrases = [
            "can you speak german", "speak german", "german please",
            "sprechen sie deutsch", "deutsch bitte", "in deutsch",
            "switch to german", "german", "wechsle zu deutsch"
        ]
        
        if any(phrase in message_lower for phrase in english_phrases):
            return "en"
        elif any(phrase in message_lower for phrase in german_phrases):
            return "de"
        
        return None
    
    async def translate_text(self, text: str, target_language: str) -> str:
        """Translate text to target language using OpenAI. Auto-detects source language."""
        if not text or not text.strip():
            return text
        
        try:
            target_lang_name = "English" if target_language == "en" else "German"
            
            # Auto-detect source language and translate
            prompt = f"""Translate the following text to {target_lang_name}. 
Auto-detect the source language (German or English) and translate accordingly.
Return ONLY the translated text, nothing else. Preserve the meaning and tone exactly.

Text to translate: "{text}"
"""
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"You are a professional translator. Translate accurately and naturally."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            if content:
                translated = content.strip()
                logger.info(f"🌐 Translated (→ {target_lang_name}): {text[:50]}... → {translated[:50]}...")
                return translated
            
            return text
        except Exception as e:
            logger.error(f"Error translating text: {str(e)}")
            return text
    
    async def get_question_in_current_language(self, question: Dict[str, Any]) -> str:
        """Get question text in the current conversation language"""
        question_text = question.get('text', question.get('description', ''))
        if not question_text:
            return ""
        
        # Detect the language of the stored question
        # Simple heuristic: check for common German words/characters
        has_german_chars = any(char in question_text for char in ['ä', 'ö', 'ü', 'ß', 'Ä', 'Ö', 'Ü'])
        common_german_words = ['der', 'die', 'das', 'und', 'ist', 'für', 'mit', 'von', 'zu', 'auf']
        has_german_words = any(word in question_text.lower() for word in common_german_words)
        
        stored_language = "de" if (has_german_chars or has_german_words) else "en"
        
        # If stored language matches current language, return as-is
        if stored_language == self.conversation_language:
            return question_text
        
        # Otherwise, translate
        return await self.translate_text(question_text, self.conversation_language)
    
    def get_message_in_current_language(self, german_text: str, english_text: str) -> str:
        """Get message in current conversation language"""
        return english_text if self.conversation_language == "en" else german_text
    
    async def refine_answer(self, raw_transcript: str, question_text: str) -> str:
        """Use OpenAI LLM to refine and normalize the user's answer"""
        try:
            prompt = f"""The user was asked: "{question_text}"
The user responded with this raw transcription (may have grammar/typos): "{raw_transcript}"

Refine this answer to be clear, grammatically correct, and professional while preserving the original meaning. 
Return ONLY the refined answer text, nothing else."""
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that refines transcriptions to be clear and professional."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            if not content:
                return raw_transcript
            refined = content.strip()
            logger.info(f"✨ Refined: {raw_transcript} → {refined}")
            return refined
            
        except Exception as e:
            logger.error(f"Error refining answer: {str(e)}")
            return raw_transcript
    
    async def validate_answer_clarity(self, answer: str) -> bool:
        """Check if answer is clear and usable (not empty, has substance)"""
        if not answer or len(answer.strip()) < 2:
            return False
        
        unclear_patterns = ["uh", "um", "er", "hmm", "well", "like", "you know"]
        answer_lower = answer.lower().strip()
        
        words = answer_lower.split()
        if len(words) <= 2 and all(word in unclear_patterns for word in words):
            return False
        
        return True
    
    @function_tool()
    async def store_answer(self, question_number: int, question_text: str, user_answer: str) -> str:
        """
        Store a user's answer to a question. Call this function IMMEDIATELY after the user answers each question.
        
        Args:
            question_number: The question number (1, 2, 3, etc.)
            question_text: The question that was asked
            user_answer: The user's answer to the question
            
        Returns:
            Confirmation message
        """
        print(f"[STORE_ANSWER] Question {question_number}: {question_text}")
        print(f"[STORE_ANSWER] Answer: {user_answer}")
        
        self.answers_collected.append({
            "question_id": question_number,
            "question_text": question_text,
            "answer": user_answer,
            "conversation_id": question_number
        })
        
        logger.info(f"✓ Stored answer for question {question_number}: {user_answer}")
        print(f"[STORE_ANSWER] Total answers stored: {len(self.answers_collected)}")
        
        return f"Answer stored successfully. Total answers: {len(self.answers_collected)}"
    
    @function_tool()    
    async def send_all_answers_to_webhook(self) -> bool:
        """
        Save all collected answers to the database.
        
        IMPORTANT: You MUST have called `store_answer` for EACH question BEFORE calling this function!
        
        IMPORTANT CONDITIONS - Call this function ONLY when ALL of these are true:
        1. ALL questions from the list have been asked and answered
        2. You have called `store_answer` for EACH answered question
        3. You have presented a SUMMARY of all answers to the user
        4. The user has EXPLICITLY confirmed the summary (e.g., "Ja", "Stimmt", "Yes", "Correct")
        
        DO NOT call this function:
        - Before all questions are answered
        - Before calling store_answer for each question
        - Before showing the summary
        - On random confirmations during the conversation
        """
        if not self.answers_collected:
            logger.warning("No answers to save")
            print("[WEBHOOK REQUEST] No answers collected - skipping webhook call")
            return True
        
        try:
            # Deduplicate answers by question_id, keeping only the last occurrence (most recent answer)
            # This handles cases where a user updates an answer during the summary confirmation phase
            deduplicated_answers = {}
            for answer in self.answers_collected:
                question_id = answer.get("question_id")
                if question_id:
                    deduplicated_answers[question_id] = answer
            
            # Convert back to list, maintaining original order as much as possible
            final_answers = list(deduplicated_answers.values())
            
            payload = {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "answers": final_answers,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            print("=" * 60)
            print("[WEBHOOK REQUEST] URL:", self.webhook_url)
            print(f"[WEBHOOK REQUEST] Data:\n{json.dumps(payload, indent=2)}")
            print(f"[WEBHOOK REQUEST] Deduplicated: {len(self.answers_collected)} -> {len(final_answers)} answers")
            print("=" * 60)
            
            logger.info(f"Sending {len(final_answers)} answers to webhook (deduplicated from {len(self.answers_collected)}): {self.webhook_url}")
            
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as http_session:
                async with http_session.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response_text = await response.text()
                    
                    print("=" * 60)
                    print(f"[WEBHOOK RESPONSE] Status: {response.status}")
                    try:
                        result = json.loads(response_text)
                        print(f"[WEBHOOK RESPONSE] Body: {json.dumps(result, indent=2)}")
                    except:
                        print(f"[WEBHOOK RESPONSE] Body: {response_text}")
                    print("=" * 60)
                    
                    if response.status == 200:
                        logger.info(f"✓ All {len(final_answers)} answers saved to database")
                        self.state = self.STATE_COMPLETED
                        print("[SESSION] Data saved successfully - scheduling disconnect...")
                        
                        # Schedule disconnect after LLM says goodbye (give 5 seconds for speech)
                        async def delayed_disconnect():
                            await asyncio.sleep(15)
                            print("[SESSION] Disconnecting from room...")
                            await self.disconnect_from_room()
                        
                        asyncio.create_task(delayed_disconnect())
                        return True
                    else:
                        logger.error(f"Webhook returned status {response.status}: {response_text}")
                        return False
        except Exception as e:
            logger.error(f"Error sending answers to webhook: {str(e)}")
            print(f"[WEBHOOK ERROR] {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def generate_summary(self) -> str:
        """Generate a summary of all collected Q&A pairs"""
        if not self.answers_collected:
            return "Keine Antworten gesammelt."
        
        summary_parts = []
        for i, qa in enumerate(self.answers_collected, 1):
            question = qa.get("question_text", "")
            answer = qa.get("answer", "")
            summary_parts.append(f"{i}. {question}: {answer}")
        
        return "\n".join(summary_parts)
    
    async def identify_answer_to_update(self, user_message: str) -> Optional[int]:
        """Use LLM to identify which answer the user wants to update based on topic/keyword"""
        try:
            # Build context of all Q&A pairs
            qa_context = []
            for i, qa in enumerate(self.answers_collected):
                qa_context.append(f"Index {i}: Question: {qa.get('question_text', '')} | Answer: {qa.get('answer', '')}")
            
            qa_list = "\n".join(qa_context)
            
            prompt = f"""The user wants to update one of their previous answers. Based on their message, identify which answer they want to change.

Available Q&A pairs:
{qa_list}

User's message: "{user_message}"

Return ONLY the index number (0, 1, 2, etc.) of the answer they want to update. If you cannot determine which answer, return -1."""

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You identify which answer a user wants to update based on keywords/topics. Return only a number."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            content = response.choices[0].message.content
            if content:
                try:
                    index = int(content.strip())
                    if 0 <= index < len(self.answers_collected):
                        logger.info(f"Identified answer to update: index {index}")
                        return index
                except ValueError:
                    pass
            
            logger.warning(f"Could not identify answer to update from: {user_message}")
            return None
            
        except Exception as e:
            logger.error(f"Error identifying answer to update: {str(e)}")
            return None
    
    async def disconnect_from_room(self):
        """Disconnect the agent from the LiveKit room"""
        try:
            if self.room:
                logger.info("Disconnecting agent from room...")
                await self.room.disconnect()
                logger.info("✓ Agent disconnected from room")
        except Exception as e:
            logger.error(f"Error disconnecting from room: {str(e)}")
    
    async def start_participant_monitor(self, room, inactivity_timeout: int = 120):
        """
        Monitor room participants and disconnect if user leaves or becomes inactive.
        
        Args:
            room: LiveKit room object
            inactivity_timeout: Seconds of inactivity before disconnecting (default: 120 = 2 minutes)
        """
        check_interval = 5  # Check every 5 seconds
        logger.info(f"Starting participant monitor (inactivity timeout: {inactivity_timeout}s)")
        
        try:
            while not self.is_disconnecting and self.state != self.STATE_COMPLETED:
                await asyncio.sleep(check_interval)
                
                # Check if participant is still in room
                if not room.remote_participants or len(room.remote_participants) == 0:
                    logger.warning("No participants found in room - user has left")
                    await self._handle_user_disconnect("User left the room")
                    break
                
                # Check for inactivity timeout
                if self.last_activity_time is not None:
                    current_time = asyncio.get_event_loop().time()
                    inactive_duration = current_time - self.last_activity_time
                    
                    if inactive_duration > inactivity_timeout:
                        logger.warning(f"User inactive for {inactive_duration:.0f}s - disconnecting")
                        await self._handle_user_disconnect(f"User inactive for {inactive_duration:.0f} seconds")
                        break
                else:
                    # If no activity tracked yet, set it to now
                    self.last_activity_time = asyncio.get_event_loop().time()
                    
        except asyncio.CancelledError:
            logger.info("Participant monitor task cancelled")
        except Exception as e:
            logger.error(f"Error in participant monitor: {str(e)}")
    
    async def _handle_user_disconnect(self, reason: str):
        """Handle user disconnection - save partial data and disconnect"""
        if self.is_disconnecting:
            return
        
        self.is_disconnecting = True
        logger.info(f"Handling user disconnect: {reason}")
        
        # If we have collected some answers, try to save them
        if self.answers_collected:
            logger.info(f"User disconnected with {len(self.answers_collected)} partial answers collected")
            # Note: We don't save partial answers automatically, but we log them
            # You can uncomment the line below if you want to save partial answers
            # try:
            #     await self.send_all_answers_to_webhook()
            # except Exception as e:
            #     logger.error(f"Error saving partial answers: {str(e)}")
        
        # Disconnect from room
        await self.disconnect_from_room()
    
    async def on_enter(self):
        """Called when agent enters the room"""
        # Initialize activity time when agent enters
        self.last_activity_time = asyncio.get_event_loop().time()
        
        current_question = self.get_current_question()
        if current_question:
            # Get question in current language (default is German)
            question_text = await self.get_question_in_current_language(current_question)
            welcome = self.get_message_in_current_language(
                f"Hallo! Schön, dass Sie da sind. Ich habe ein paar Fragen für Sie. {question_text}",
                f"Hello! Nice to have you here. I have a few questions for you. {question_text}"
            )
            logger.info(f"🤖 AGENT: {welcome}")
            await self.session.generate_reply(
                instructions=f"Say exactly this: {welcome}",
                allow_interruptions=True,
            )
        else:
            greeting = self.get_message_in_current_language(
                "Begrüße den Nutzer herzlich und biete deine Hilfe an.",
                "Greet the user warmly and offer your assistance."
            )
            logger.info("🤖 AGENT: [Greeting user and offering assistance]")
            await self.session.generate_reply(
                instructions=greeting,
                allow_interruptions=True,
            )
    
    async def on_user_message(self, message: str):
        """Handle user messages based on current state"""
        try:
            # Update last activity time
            self.last_activity_time = asyncio.get_event_loop().time()
            
            logger.info(f"🎤 USER: {message} [State: {self.state}, Lang: {self.conversation_language}]")
            
            # Check for language switch request
            requested_language = self.detect_language_switch_request(message)
            if requested_language and requested_language != self.conversation_language:
                self.conversation_language = requested_language
                lang_name = "English" if requested_language == "en" else "German"
                logger.info(f"🌐 Language switched to {lang_name}")
                
                # Acknowledge language switch naturally (don't mention it explicitly per instructions)
                # Just continue with the conversation in the new language
                if self.state == self.STATE_COLLECTING:
                    # If we're collecting, continue with current question in new language
                    await self._handle_collecting(message)
                elif self.state == self.STATE_AWAITING_FINAL_CONFIRMATION:
                    await self._handle_final_confirmation(message)
                elif self.state == self.STATE_AWAITING_UPDATE_ANSWER:
                    await self._handle_update_answer(message)
                else:
                    # Just acknowledge and continue
                    await self._handle_collecting(message)
                return
            
            # Route to appropriate handler based on state
            if self.state == self.STATE_COLLECTING:
                await self._handle_collecting(message)
            elif self.state == self.STATE_AWAITING_FINAL_CONFIRMATION:
                await self._handle_final_confirmation(message)
            elif self.state == self.STATE_AWAITING_UPDATE_ANSWER:
                await self._handle_update_answer(message)
            elif self.state == self.STATE_COMPLETED:
                # Session is done, politely end
                goodbye = self.get_message_in_current_language(
                    "Die Sitzung ist abgeschlossen. Auf Wiedersehen!",
                    "The session is complete. Goodbye!"
                )
                logger.info(f"🤖 AGENT: {goodbye}")
                await self.session.generate_reply(
                    instructions=f"Say exactly this: {goodbye}",
                    allow_interruptions=True,
                )
                
        except Exception as e:
            logger.error(f"Error in on_user_message: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            error_msg = self.get_message_in_current_language(
                "Es tut mir leid, es gibt gerade ein technisches Problem. Bitte versuchen Sie es noch einmal.",
                "I'm sorry, there's a technical problem right now. Please try again."
            )
            logger.info(f"🤖 AGENT: {error_msg}")
            await self.session.generate_reply(
                instructions=error_msg,
                allow_interruptions=True,
            )
    
    async def _handle_collecting(self, message: str):
        """Handle message during question collection phase"""
        # All questions answered - move to final confirmation
        if self.current_question_index >= len(self.questions):
            await self._present_summary()
            return
        
        question = self.get_current_question()
        if not question:
            return
        
        question_id = question.get("id")
        # Get question in current language
        question_text = await self.get_question_in_current_language(question)
        is_mandatory = question.get("is_mandatory", False)
        
        if not question_text:
            logger.warning(f"Empty question text for question {question_id}")
            self.current_question_index += 1
            await self._ask_next_question()
            return
        
        raw_answer = message.strip()
        
        # Handle empty answer
        if not raw_answer:
            if self.retry_count < self.max_retries - 1:
                self.retry_count += 1
                if is_mandatory:
                    retry_msg = self.get_message_in_current_language(
                        "Diese Information ist wichtig für die Empfehlung. Könnten Sie mir bitte antworten?",
                        "This information is important for the recommendation. Could you please answer?"
                    )
                else:
                    retry_msg = self.get_message_in_current_language(
                        "Das habe ich leider nicht verstanden. Könnten Sie das bitte noch einmal sagen?",
                        "I'm sorry, I didn't understand that. Could you please say it again?"
                    )
                logger.info(f"🤖 AGENT: {retry_msg}")
                await self.session.generate_reply(
                    instructions=retry_msg,
                    allow_interruptions=True,
                )
                return
            else:
                # We've reached max retries
                if is_mandatory:
                    logger.warning(f"Mandatory question {question_id} not answered after {self.max_retries} attempts")
                    # For mandatory questions, try one more time with a stronger message
                    self.retry_count += 1
                    retry_msg = self.get_message_in_current_language(
                        f"Ich verstehe, dass Sie diese Information vielleicht nicht sofort haben. Diese Information ist jedoch wichtig für die Empfehlung. Könnten Sie mir bitte antworten: {question_text}",
                        f"I understand that you might not have this information immediately. However, this information is important for the recommendation. Could you please answer: {question_text}"
                    )
                    logger.info(f"🤖 AGENT: {retry_msg}")
                    await self.session.generate_reply(
                        instructions=f"Say exactly this: {retry_msg}",
                        allow_interruptions=True,
                    )
                    return
                else:
                    logger.warning(f"No answer received for question {question_id}")
                    self.current_question_index += 1
                    self.retry_count = 0
                    await self._ask_next_question()
                    return
        
        # Handle unclear answer
        if not await self.validate_answer_clarity(raw_answer):
            if self.retry_count < self.max_retries - 1:
                self.retry_count += 1
                if is_mandatory:
                    clarity_msg = self.get_message_in_current_language(
                        "Diese Information ist wichtig für die Empfehlung. Könnten Sie mir das etwas genauer erklären?",
                        "This information is important for the recommendation. Could you explain this in more detail?"
                    )
                else:
                    clarity_msg = self.get_message_in_current_language(
                        "Das habe ich nicht ganz verstanden. Könnten Sie mir das etwas genauer erklären?",
                        "I didn't quite understand that. Could you explain it in more detail?"
                    )
                logger.info(f"🤖 AGENT: {clarity_msg}")
                await self.session.generate_reply(
                    instructions=clarity_msg,
                    allow_interruptions=True,
                )
                return
            else:
                if is_mandatory:
                    logger.warning(f"Answer not clear for mandatory question {question_id}")
                    # Keep trying or move on after max retries
                else:
                    logger.warning(f"Answer not clear for question {question_id}")
                    self.current_question_index += 1
                    self.retry_count = 0
                    await self._ask_next_question()
                    return
        
        # Refine and store the answer locally
        refined_answer = await self.refine_answer(raw_answer, question_text)
        
        # Store answer for bulk save later - store translated question text (the version actually asked)
        self.answers_collected.append({
            "question_id": question_id,
            "question_text": question_text,  # Store translated version that was asked
            "answer": refined_answer,
            "conversation_id": self.conversation_id
        })
        logger.info(f"✓ Collected answer for question {question_id}: {refined_answer}")
        
        # Remove from mandatory pending list if it was there
        question_index = self.current_question_index
        if question_index in self.mandatory_questions_pending:
            self.mandatory_questions_pending.remove(question_index)
            logger.info(f"✓ Mandatory question {question_id} answered, removed from pending list")
        
        self.conversation_id += 1
        self.current_question_index += 1
        self.retry_count = 0
        
        # Move to next question or present summary
        await self._ask_next_question()
    
    async def _handle_final_confirmation(self, message: str):
        """Handle user response to final summary"""
        user_lower = message.lower().strip()
        
        # Check for confirmation phrases (both languages)
        confirmation_phrases = ["ja", "yes", "correct", "richtig", "stimmt", "passt", "korrekt", "okay", "ok", "genau", "alles richtig", "speichern", "save", "all correct"]
        
        # Check for update/change phrases (both languages)
        update_phrases = ["ändern", "change", "update", "korrigieren", "falsch", "wrong", "nein", "no", "nicht richtig", "änderung", "modify", "edit"]
        
        is_confirmed = any(phrase in user_lower for phrase in confirmation_phrases)
        wants_update = any(phrase in user_lower for phrase in update_phrases)
        
        if is_confirmed and not wants_update:
            # User confirmed - save and disconnect
            logger.info("User confirmed all answers, saving to database...")
            success = await self.send_all_answers_to_webhook()
            
            if success:
                self.state = self.STATE_COMPLETED
                goodbye_msg = self.get_message_in_current_language(
                    "Wunderbar! Alle Ihre Antworten wurden gespeichert. Vielen Dank für Ihre Zeit. Auf Wiedersehen!",
                    "Wonderful! All your answers have been saved. Thank you for your time. Goodbye!"
                )
                logger.info(f"🤖 AGENT: {goodbye_msg}")
                await self.session.generate_reply(
                    instructions=f"Say exactly this: {goodbye_msg}",
                    allow_interruptions=True,
                )
                # Disconnect from room after a short delay
                await asyncio.sleep(2)
                await self.disconnect_from_room()
            else:
                error_msg = self.get_message_in_current_language(
                    "Es gab leider ein Problem beim Speichern. Möchten Sie es noch einmal versuchen?",
                    "Unfortunately, there was a problem saving. Would you like to try again?"
                )
                logger.info(f"🤖 AGENT: {error_msg}")
                await self.session.generate_reply(
                    instructions=f"Say exactly this: {error_msg}",
                    allow_interruptions=True,
                )
        
        elif wants_update:
            # User wants to update - identify which answer
            update_index = await self.identify_answer_to_update(message)
            
            if update_index is not None:
                self.update_index = update_index
                self.state = self.STATE_AWAITING_UPDATE_ANSWER
                qa = self.answers_collected[update_index]
                question_text = qa.get("question_text", "")
                current_answer = qa.get("answer", "")
                
                # Translate question text if needed for display
                display_question = await self.translate_text(question_text, self.conversation_language) if question_text else ""
                
                ask_update_msg = self.get_message_in_current_language(
                    f"Alles klar. Die aktuelle Antwort für '{display_question}' ist: '{current_answer}'. Was ist die richtige Antwort?",
                    f"All right. The current answer for '{display_question}' is: '{current_answer}'. What is the correct answer?"
                )
                logger.info(f"🤖 AGENT: {ask_update_msg}")
                await self.session.generate_reply(
                    instructions=f"Say exactly this: {ask_update_msg}",
                    allow_interruptions=True,
                )
            else:
                # Could not identify - ask user to specify
                clarify_msg = self.get_message_in_current_language(
                    "Welche Antwort möchten Sie ändern? Bitte sagen Sie mir das Thema oder die Frage.",
                    "Which answer would you like to change? Please tell me the topic or the question."
                )
                logger.info(f"🤖 AGENT: {clarify_msg}")
                await self.session.generate_reply(
                    instructions=f"Say exactly this: {clarify_msg}",
                    allow_interruptions=True,
                )
        else:
            # Unclear response - ask again
            unclear_msg = self.get_message_in_current_language(
                "Sind alle Angaben korrekt? Sagen Sie 'ja' zum Speichern oder nennen Sie mir, was Sie ändern möchten.",
                "Are all the details correct? Say 'yes' to save or tell me what you would like to change."
            )
            logger.info(f"🤖 AGENT: {unclear_msg}")
            await self.session.generate_reply(
                instructions=f"Say exactly this: {unclear_msg}",
                allow_interruptions=True,
            )
    
    async def _handle_update_answer(self, message: str):
        """Handle the new answer from user for update"""
        if self.update_index is None:
            self.state = self.STATE_AWAITING_FINAL_CONFIRMATION
            await self._present_summary()
            return
        
        raw_answer = message.strip()
        
        if not raw_answer or not await self.validate_answer_clarity(raw_answer):
            retry_msg = self.get_message_in_current_language(
                "Das habe ich nicht verstanden. Bitte geben Sie die neue Antwort noch einmal an.",
                "I didn't understand that. Please provide the new answer again."
            )
            logger.info(f"🤖 AGENT: {retry_msg}")
            await self.session.generate_reply(
                instructions=retry_msg,
                allow_interruptions=True,
            )
            return
        
        # Refine and update the answer
        qa = self.answers_collected[self.update_index]
        question_text = qa.get("question_text", "")
        refined_answer = await self.refine_answer(raw_answer, question_text)
        
        # Update the answer
        self.answers_collected[self.update_index]["answer"] = refined_answer
        logger.info(f"✓ Updated answer for index {self.update_index}: {refined_answer}")
        
        # Reset update state
        self.update_index = None
        self.state = self.STATE_AWAITING_FINAL_CONFIRMATION
        
        # Re-present the full summary
        confirm_update_msg = self.get_message_in_current_language(
            "Verstanden, ich habe die Antwort aktualisiert.",
            "Understood, I have updated the answer."
        )
        logger.info(f"🤖 AGENT: {confirm_update_msg}")
        await self.session.generate_reply(
            instructions=f"Say exactly this: {confirm_update_msg}",
            allow_interruptions=True,
        )
        
        await asyncio.sleep(1)
        await self._present_summary()
    
    async def _present_summary(self):
        """Present summary of all answers and ask for final confirmation"""
        self.state = self.STATE_AWAITING_FINAL_CONFIRMATION
        
        summary = self.generate_summary()
        
        # Translate summary if needed
        if self.conversation_language == "en":
            summary = await self.translate_text(summary, "en")
        
        summary_msg = self.get_message_in_current_language(
            f"Hier ist die Zusammenfassung Ihrer Antworten:\n\n{summary}\n\nIst alles korrekt? Sagen Sie 'ja' zum Speichern oder nennen Sie mir, was Sie ändern möchten.",
            f"Here is the summary of your answers:\n\n{summary}\n\nIs everything correct? Say 'yes' to save or tell me what you would like to change."
        )
        logger.info(f"🤖 AGENT: Presenting summary for confirmation")
        await self.session.generate_reply(
            instructions=f"Read this summary to the user and ask for confirmation: {summary_msg}",
            allow_interruptions=True,
        )
    
    async def _ask_next_question(self):
        """Ask the next question or present summary for final confirmation"""
        # Check if there are pending mandatory questions that need to be re-asked
        if self.mandatory_questions_pending and self.current_question_index >= len(self.questions):
            # Re-ask mandatory questions that weren't answered
            pending_idx = self.mandatory_questions_pending[0]
            if pending_idx < len(self.questions):
                pending_question = self.questions[pending_idx]
                # Get question in current language
                pending_question_text = await self.get_question_in_current_language(pending_question)
                retry_mandatory_msg = self.get_message_in_current_language(
                    f"Ich benötige noch eine wichtige Information: {pending_question_text}",
                    f"I still need an important piece of information: {pending_question_text}"
                )
                logger.info(f"🤖 AGENT: Re-asking mandatory question: {retry_mandatory_msg}")
                await self.session.generate_reply(
                    instructions=f"Say exactly this: {retry_mandatory_msg}",
                    allow_interruptions=True,
                )
                # Temporarily set current_question_index to re-ask this question
                self.current_question_index = pending_idx
                self.retry_count = 0
                return
        
        if self.current_question_index < len(self.questions):
            next_question = self.get_current_question()
            if next_question:
                # Get question in current language
                next_question_text = await self.get_question_in_current_language(next_question)
                is_mandatory = next_question.get('is_mandatory', False)
                
                if is_mandatory:
                    transition_msg = self.get_message_in_current_language(
                        f"Gut, danke. Diese nächste Frage ist wichtig: {next_question_text}",
                        f"Good, thank you. This next question is important: {next_question_text}"
                    )
                else:
                    transition_msg = self.get_message_in_current_language(
                        f"Gut, danke. {next_question_text}",
                        f"Good, thank you. {next_question_text}"
                    )
                logger.info(f"🤖 AGENT: {transition_msg}")
                await self.session.generate_reply(
                    instructions=f"Say exactly this: {transition_msg}",
                    allow_interruptions=True,
                )
        else:
            # All questions answered - present summary for final confirmation
            await self._present_summary()
    
server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session()  
async def entrypoint(ctx: JobContext):
    try:
        logger.info(f"Agent started for job {ctx.job.id}")
        
        await ctx.connect()
        logger.info(f"Connected to room: {ctx.room.name}")
        
        metadata = await parse_metadata(ctx)
        if not metadata:
            logger.error("Failed to parse metadata, exiting")
            return
        
        session_id = metadata["session_id"]
        user_id = metadata["user_id"]
        questions = metadata["questions"]
        webhook_url = metadata["backend_webhook"]
        
        logger.info(f"Session: {session_id}, User: {user_id}, Questions: {len(questions)}")
        
        logger.info("Waiting for participant to join...")
        participant_connected = False
        max_wait_time = 300
        wait_interval = 2
        waited = 0
        
        while not participant_connected and waited < max_wait_time:
            if ctx.room.remote_participants:
                participant = list(ctx.room.remote_participants.values())[0]
                logger.info(f"Participant joined: {participant.identity}")
                participant_connected = True
                break
            await asyncio.sleep(wait_interval)
            waited += wait_interval
        
        if not participant_connected:
            logger.warning("No participant joined within timeout period")
            return
        
        await asyncio.sleep(2)
        
        deepgram_key = os.getenv('DEEPGRAM_API_KEY')
        if deepgram_key:
            logger.info("Testing Deepgram API connection...")
            is_valid = await test_deepgram_connection(deepgram_key.strip())
            if not is_valid:
                logger.error("Deepgram API key validation failed. Please check your API key.")
                return
        
        deepgram_key = os.getenv('DEEPGRAM_API_KEY')
        if not deepgram_key:
            logger.error("DEEPGRAM_API_KEY not found in environment variables")
            raise ValueError("DEEPGRAM_API_KEY is required")
        
        if len(deepgram_key) < 20:
            logger.error(f"Invalid DEEPGRAM_API_KEY format (length: {len(deepgram_key)})")
            raise ValueError("DEEPGRAM_API_KEY appears to be invalid")
        
        os.environ['DEEPGRAM_API_KEY'] = deepgram_key
        logger.info(f"Deepgram API key configured (length: {len(deepgram_key)}, prefix: {deepgram_key[:8]}...)")
        
        session: AgentSession = AgentSession(
            stt=deepgram.STTv2(
                model="flux-general-en",
                eager_eot_threshold=0.4,
            ),
            llm=openai.LLM(model="gpt-4o", temperature=0.4),
            tts=deepgram.TTS(
                model="aura-2-thalia-en",  
            ),
            vad=ctx.proc.userdata["vad"],
            preemptive_generation=True,
        )
        
        agent = DefaultAgent(questions, session_id, user_id, webhook_url, room=ctx.room)
        
        # Start participant monitoring task
        # Monitor checks every 5 seconds for participant presence and inactivity
        inactivity_timeout = int(os.getenv('AGENT_INACTIVITY_TIMEOUT', '60'))  # Default 1 minutes
        agent.monitor_task = asyncio.create_task(
            agent.start_participant_monitor(ctx.room, inactivity_timeout=inactivity_timeout)
        )
        
        # Start the session - this will keep the agent active
        try:
            await session.start(
                agent=agent,
                room=ctx.room,
                room_options=room_io.RoomOptions(
                    audio_input=room_io.AudioInputOptions(
                        noise_cancellation=noise_cancellation.BVC()
                    ),
                ),
            )
        finally:
            # Cancel monitor task when session ends
            if agent.monitor_task and not agent.monitor_task.done():
                agent.monitor_task.cancel()
                try:
                    await agent.monitor_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Agent session completed")
        
    except Exception as e:
        logger.error(f"Error in agent entrypoint: {str(e)}")
        import traceback
        traceback.print_exc()
if __name__ == "__main__":
    env_path = Path(__file__).parent / 'dev.env'
    if env_path.exists():
        load_dotenv(env_path)
        logging.info(f"Loaded environment from {env_path}")
    else:
        logging.warning(f"dev.env not found at {env_path}, trying default .env")
        load_dotenv()
    
    required_vars = ['LIVEKIT_URL', 'LIVEKIT_API_KEY', 'LIVEKIT_API_SECRET', 'OPENAI_API_KEY', 'DEEPGRAM_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        exit(1)
    
    livekit_url = os.getenv('LIVEKIT_URL')
    if not livekit_url:
        logger.error("LIVEKIT_URL is required")
        exit(1)
    
    logger.info(f"Starting LiveKit agent with URL: {livekit_url}")
    
    if not livekit_url.startswith(('ws://', 'wss://')):
        logger.error(f"Invalid LIVEKIT_URL format: {livekit_url}")
        exit(1)
    
    cli.run_app(server)