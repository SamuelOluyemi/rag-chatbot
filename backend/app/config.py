# For production ready 

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set. Add it to your .env or Cloud Run env vars.")

EMBED_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"
EMBED_DIM = 1536
TOP_K = 4

# Debug print (optional, remove later)
print("OPENAI_API_KEY loaded:", bool(OPENAI_API_KEY))