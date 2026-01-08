"""LLM component initialization for the text-based agent."""

import os
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from app.core.config import settings

# Set OpenAI API key in environment (ChatOpenAI reads from environment by default)
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

# Initialize OpenAI LLM
llm = ChatOpenAI(
    model="gpt-4o",
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()],
    temperature=0.7,
)

