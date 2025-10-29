import os
from dotenv import load_dotenv

# Load .env file if it exists (for local development)
# In production (Railway), environment variables are injected directly
load_dotenv(override=False)

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.5"))

# App
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# CORS - Frontend URL
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Arize Phoenix
ARIZE_SPACE_ID = os.getenv("ARIZE_SPACE_ID")
ARIZE_API_KEY = os.getenv("ARIZE_API_KEY")
ARIZE_PROJECT_NAME = os.getenv("ARIZE_PROJECT_NAME", "trippy-multi-city")

# Validation
if not OPENAI_API_KEY:
    # Debug: print all environment variables that start with OPENAI
    import sys
    print("❌ OPENAI_API_KEY is not set!", file=sys.stderr)
    print(f"Available env vars: {[k for k in os.environ.keys() if 'OPENAI' in k]}", file=sys.stderr)
    raise ValueError("❌ OPENAI_API_KEY must be set as environment variable")

print(f"✅ Config loaded: {OPENAI_MODEL}, Environment: {ENVIRONMENT}")
