"""LLM component initialization for subsidy calculation."""

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI LLM for subsidy calculation
llm = ChatOpenAI(
    model="gpt-4.1",
    streaming=False,
    temperature=0.2,  # Lower temperature for more deterministic subsidy evaluation
    max_tokens=4096
)
