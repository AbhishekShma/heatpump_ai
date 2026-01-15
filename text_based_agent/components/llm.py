"""LLM component initialization for the text-based agent."""

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize OpenAI LLM
llm = ChatOpenAI(
    model="gpt-4.1",
    streaming=False,
    temperature=0.7,
    max_tokens=4096
)

