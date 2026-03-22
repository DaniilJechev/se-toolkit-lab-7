"""Configuration module for the bot."""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class BotConfig:
    """Bot configuration loaded from environment variables."""
    
    def __init__(self):
        # Load .env.bot.secret if it exists
        env_file = Path(__file__).parent / ".env.bot.secret"
        if env_file.exists():
            load_dotenv(env_file)
        
        # Telegram Bot Token
        self.bot_token: str = os.getenv("BOT_TOKEN", "")
        
        # LMS API Configuration
        self.lms_api_url: str = os.getenv("LMS_API_URL", "http://localhost:42002")
        self.lms_api_key: str = os.getenv("LMS_API_KEY", "")
        
        # LLM API Configuration
        self.llm_api_key: str = os.getenv("LLM_API_KEY", "")
        self.llm_api_base_url: str = os.getenv("LLM_API_BASE_URL", "http://localhost:42005/v1")
        self.llm_model: str = os.getenv("LLM_API_MODEL", "coder-model")
    
    @property
    def is_test_mode(self) -> bool:
        """Check if running in test mode (no Telegram connection)."""
        return not self.bot_token
    
    def validate(self) -> bool:
        """Validate required configuration."""
        if not self.lms_api_key:
            raise ValueError("LMS_API_KEY is required")
        return True


# Global config instance
config = BotConfig()


def get_config() -> BotConfig:
    """Get the global configuration instance."""
    return config
