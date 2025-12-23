"""
Tools for the LiveKit voice agent.
"""

from datetime import datetime
from livekit.agents import function_tool, RunContext


@function_tool()
async def get_current_time(
    context: RunContext,  # LiveKit provides this automatically
) -> str:
    """
    Returns the current UTC time as an ISO8601 string.
    """
    now = datetime.utcnow()
    return now.isoformat() + "Z"


