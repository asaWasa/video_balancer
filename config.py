from dotenv import load_dotenv
import os


load_dotenv()


SENTRY_DSN = os.getenv("SENTRY_DSN")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_CACHE_DB = int(os.getenv("REDIS_CACHE_DB", "4"))

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5434/video_balancer",
)
CDN_HOST = os.getenv("CDN_HOST", "cdn.example.com")
DEFAULT_CDN_RATIO = int(os.getenv("DEFAULT_CDN_RATIO", "9"))
DEFAULT_ORIGIN_RATIO = int(os.getenv("DEFAULT_ORIGIN_RATIO", "1"))
