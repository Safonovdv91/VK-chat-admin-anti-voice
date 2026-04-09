import os

from dotenv import load_dotenv

load_dotenv()

MAX_VOICE_DURATION: int = int(os.getenv ("MAX_VOICE_DURATION",0))
MAX_VIDEO_DURATION: int = int(os.getenv ("MAX_VIDEO_DURATION",0))
WARNING_TTL: int = int(os.getenv("WARNING_TTL",5))           # секунды до удаления предупреждения
