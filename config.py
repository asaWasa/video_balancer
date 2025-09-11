from dotenv import load_dotenv
import os


load_dotenv()


SENTRY_DSN = os.getenv("SENTRY_DSN")
