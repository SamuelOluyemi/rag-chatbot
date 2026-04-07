# # before production ready 

# import os
# from dotenv import load_dotenv

# # load_dotenv()

# # Load .env manually
# # load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

# # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# OPENAI_API_KEY='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'

# EMBED_MODEL = "text-embedding-3-small"
# # LLM_MODEL = "gpt-4o-mini"
# # LLM_MODEL = "gpt-5" # only accessible for paid or not low-tier accounts
# LLM_MODEL = "gpt-5"
# # EMBED_DIM = 1536
# EMBED_DIM = 384

# # Debug print (optional, remove later)
# print("OPENAI_API_KEY loaded:", bool(OPENAI_API_KEY))

# For production ready 

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



LLM_MODEL = "gpt-4o-mini"
# EMBED_DIM = 1536
EMBED_DIM = 384
TOP_K = 4

# Debug print (optional, remove later)
print("OPENAI_API_KEY loaded:", bool(OPENAI_API_KEY))