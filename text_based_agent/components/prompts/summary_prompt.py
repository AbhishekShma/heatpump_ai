"""Summary prompts for generating conversation summaries."""

SUMMARY_PROMPT_TEMPLATE = """Review the conversation history above and the following questions:

{questions}

If all questions have been answered by the user, create a summary with the following structure:
1. Start with exposition text explaining that all questions have been completed (e.g., "Thank you! I've gathered all the information I need. Here's a summary of your responses:")
2. Then provide a concise summary of the user's responses to each question, clearly showing each question and the corresponding answer
3. End with a brief statement about what will happen next (e.g., "I'll use this information to provide you with a personalized heat pump recommendation.")

If not all questions are answered, do not output anything at all. Return an empty response with no text whatsoever."""
