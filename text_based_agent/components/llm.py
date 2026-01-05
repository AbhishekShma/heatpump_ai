"""LLM component initialization for the text-based agent."""

from langchain_openai import ChatOpenAI
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize OpenAI LLM
llm = ChatOpenAI(
    model="gpt-4o",
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()],
    temperature=0.7,
    max_tokens=4096
)

