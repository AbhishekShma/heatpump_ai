"""Confirmation detection prompt for the text-based agent."""

CONFIRMATION_DETECTION_PROMPT = """Analyze the conversation history and determine:

1. Has a confirmation request been made? (Has the assistant asked the user to confirm their answers?)
2. If a confirmation request was made, has the user responded to it?
3. If the user responded, are they satisfied with their answers?
4. Is the user's response ambiguous or unclear?

CRITICAL: Distinguish between summaries and confirmation requests:
- A SUMMARY is when the assistant lists answers but does NOT ask for confirmation - this is NOT a confirmation request
- A CONFIRMATION REQUEST must explicitly ask the user to confirm, verify, or ask if they want to change anything
- Examples of summaries (NOT confirmation requests):
  * "Here's a summary of your responses: [list] I'll use this information to provide a recommendation"
  * "I've gathered all the information. Here's what you told me: [list]"
- Examples of confirmation requests (IS a confirmation request):
  * "Is everything correct?" / "Ist alles korrekt?"
  * "Would you like to change anything?" / "Möchten Sie etwas ändern?"
  * "Please confirm if this information is correct" / "Bitte bestätigen Sie, ob diese Informationen korrekt sind"
  * "Can you confirm these answers?" / "Können Sie diese Antworten bestätigen?"

Respond ONLY with a JSON object in this exact format:
{{
    "confirmation_requested": true/false,
    "user_responded": true/false,
    "user_satisfied": true/false,
    "needs_clarification": true/false
}}

CRITICAL RULES:
- user_satisfied = TRUE if user explicitly confirms OR indicates they're done:
  * Explicit confirmation: "yes", "yes correct", "yes everything is correct", "confirmed", "that's correct", "all correct"
  * Indicates done/no changes: "no updates", "no changes", "no change", "that's fine", "that's okay", "proceed", "go ahead"
  * Accepts as-is: "all set", "all good", "looks good", "sounds good", "okay", "fine", "nothing to change"
  * German: "ja", "ja korrekt", "alles korrekt", "stimmt", "keine Änderungen", "in Ordnung"
  
- user_satisfied = FALSE if user explicitly wants changes:
  * "no I want to change", "change X", "modify Y", "update Z", "fix this", "wrong", "incorrect"
  * "nein ich möchte ändern", "ändern", "korrigieren", "falsch"
  
- needs_clarification = TRUE if user response is ambiguous:
  * Single words like "no" or "yes" without context (could mean either)
  * Unclear responses that could mean either confirmation or wanting changes
  * Responses that don't clearly indicate satisfaction or dissatisfaction
  
- If needs_clarification is true, user_satisfied should be false (default to not satisfied until clarified)
- IMPORTANT: "no updates" or "no changes" typically means user is satisfied (no changes needed) - set user_satisfied to true

If user wants to change something, user_satisfied should be false.
If user confirms everything is correct, user_satisfied should be true.
If response is ambiguous, needs_clarification should be true."""
