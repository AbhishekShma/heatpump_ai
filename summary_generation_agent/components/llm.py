"""LLM component initialization for the summary generation agent."""

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    max_tokens=2048
)
