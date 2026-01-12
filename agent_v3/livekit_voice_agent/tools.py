"""
Tools for the LiveKit voice agent.
"""

from datetime import datetime
from livekit.agents import function_tool, RunContext
import sys
from pathlib import Path

# Add parent directory to path to import json extraction tool
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from heat_load_calculation_tool.json_extraction_function_tool import json_extraction_tool


@function_tool()
async def get_current_time(
    context: RunContext,  # LiveKit provides this automatically
) -> str:
    """
    Returns the current UTC time as an ISO8601 string.
    """
    now = datetime.utcnow()
    return now.isoformat() + "Z"


