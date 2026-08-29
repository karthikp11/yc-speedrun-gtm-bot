import os
from pydantic import BaseModel

class AppConfig(BaseModel):
    SLACK_BOT_TOKEN: str = os.getenv("SLACK_BOT_TOKEN", "xoxb-your-bot-token")
    SLACK_APP_TOKEN: str = os.getenv("SLACK_APP_TOKEN", "xapp-your-app-token")
    SLACK_CHANNEL_ID: str = os.getenv("SLACK_CHANNEL_ID", "C01ABC23DEF")
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "gtm_signals.db")
    POLL_INTERVAL_HOURS: int = int(os.getenv("POLL_INTERVAL_HOURS", "8"))
    TELEMETRY_PORT: int = int(os.getenv("TELEMETRY_PORT", "8080"))
    
    TWITTER_BEARER_TOKEN: str = os.getenv("TWITTER_BEARER_TOKEN", "")
    LINKEDIN_SESSION_COOKIE: str = os.getenv("LINKEDIN_SESSION_COOKIE", "")

config = AppConfig()
