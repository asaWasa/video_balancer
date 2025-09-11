from config import (
    SENTRY_DSN,
)

from fastapi import FastAPI
import sentry_sdk
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[
        LoggingIntegration(),
        HttpxIntegration(),
    ],
    traces_sample_rate=0.1,
)

app = FastAPI()
