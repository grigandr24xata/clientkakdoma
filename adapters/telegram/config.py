import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
