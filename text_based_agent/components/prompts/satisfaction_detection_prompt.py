"""Satisfaction detection prompt for the text-based agent."""

SATISFACTION_DETECTION_PROMPT = """Analyze the user's response to the confirmation request and determine if they are satisfied (want to proceed) or want to make changes.

The user was asked to confirm if their information is correct or if they want to change anything.

Respond ONLY with a JSON object in this exact format:
{{
    "user_satisfied": true/false
}}

CRITICAL RULES:
- user_satisfied = TRUE if the user indicates they are done/ready to proceed:
  * Explicit confirmation: "yes", "correct", "confirmed", "all good", "that's right"
  * Indicates no changes needed: "no updates", "no changes", "no change", "that's fine", "that's okay"
  * Ready to proceed: "proceed", "go ahead", "all set", "looks good", "sounds good", "okay", "fine"
  * Accepts as-is: "nothing to change", "no modifications", "it's fine", "good to go"
  * German: "ja", "korrekt", "keine Änderungen", "in Ordnung", "passt"
  
- user_satisfied = FALSE if the user wants to make changes:
  * "change X", "modify Y", "update Z", "fix this", "wrong", "incorrect", "not right"
  * "nein ich möchte ändern", "ändern", "korrigieren", "falsch"
  
- Consider context: "no updates" typically means "no changes needed" (satisfied)
- When in doubt, default to false (not satisfied)"""
