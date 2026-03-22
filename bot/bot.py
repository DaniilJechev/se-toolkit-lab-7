#!/usr/bin/env python3
"""
Telegram Bot for LMS Analytics

Entry point with --test mode support for offline testing.

Usage:
    uv run bot.py --test "/start"     # Test mode
    uv run bot.py                      # Telegram mode
"""
import sys
import argparse
import asyncio
from typing import Optional

# Import handlers
from handlers.start import handle_start
from handlers.help import handle_help
from handlers.health import handle_health
from handlers.labs import handle_labs
from handlers.scores import handle_scores
from handlers.submissions import handle_submissions
from handlers.default import handle_unknown

# Import config
from config import get_config
from services.lms_client import LMSClient


async def process_message_async(text: str) -> str:
    """
    Process message with async operations (LMS API, LLM).
    
    Args:
        text: User message text
    
    Returns:
        Response string
    """
    text = text.strip()
    config = get_config()
    
    # Create LMS client
    lms = LMSClient(config.lms_api_url, config.lms_api_key)
    
    # Handle slash commands
    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        command = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else None
        
        if command == "/start":
            return handle_start()
        elif command == "/help":
            return handle_help()
        elif command == "/health":
            return await handle_health(lms)
        elif command == "/labs":
            return await handle_labs(lms)
        elif command == "/scores":
            return await handle_scores(lms, arg)
        elif command == "/submissions":
            return await handle_submissions(lms, arg)
        else:
            return handle_unknown(command)
    
    # Natural language - simple keyword matching for now
    text_lower = text.lower()
    if "lab" in text_lower and ("available" in text_lower or "list" in text_lower):
        return await handle_labs(lms)
    elif "score" in text_lower:
        # Try to extract lab name
        import re
        match = re.search(r'lab[- ]?\d+', text_lower, re.IGNORECASE)
        lab = match.group(0) if match else None
        return await handle_scores(lms, lab)
    elif "help" in text_lower:
        return handle_help()
    else:
        return handle_unknown(text)


def run_test_mode(command: str) -> None:
    """
    Run bot in test mode - process command and print result.
    
    Args:
        command: Command to test (e.g., "/start", "/help")
    """
    response = asyncio.run(process_message_async(command))
    print(response)
    sys.exit(0)


async def run_telegram_bot() -> None:
    """Run the bot with Telegram polling."""
    try:
        from aiogram import Bot, Dispatcher, types
        from aiogram.filters import CommandStart, Command
    except ImportError:
        print("Error: aiogram not installed. Run: uv sync")
        sys.exit(1)
    
    config = get_config()
    
    if not config.bot_token:
        print("Error: BOT_TOKEN not set. Cannot run in Telegram mode.")
        sys.exit(1)
    
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()
    
    @dp.message(CommandStart())
    async def on_start(message: types.Message):
        response = handle_start(message.from_user.first_name)
        await message.answer(response)
    
    @dp.message(Command("help"))
    async def on_help(message: types.Message):
        await message.answer(handle_help())
    
    @dp.message(Command("health"))
    async def on_health(message: types.Message):
        lms = LMSClient(config.lms_api_url, config.lms_api_key)
        response = await handle_health(lms)
        await message.answer(response)
    
    @dp.message(Command("labs"))
    async def on_labs(message: types.Message):
        lms = LMSClient(config.lms_api_url, config.lms_api_key)
        response = await handle_labs(lms)
        await message.answer(response)
    
    @dp.message(Command("scores"))
    async def on_scores(message: types.Message):
        lms = LMSClient(config.lms_api_url, config.lms_api_key)
        lab_name = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        response = await handle_scores(lms, lab_name)
        await message.answer(response)
    
    @dp.message(Command("submissions"))
    async def on_submissions(message: types.Message):
        lms = LMSClient(config.lms_api_url, config.lms_api_key)
        lab_name = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        response = await handle_submissions(lms, lab_name)
        await message.answer(response)
    
    @dp.message()
    async def on_message(message: types.Message):
        lms = LMSClient(config.lms_api_url, config.lms_api_key)
        response = await process_message_async(message.text)
        await message.answer(response)
    
    print(f"Bot started. Polling...")
    await dp.start_polling(bot)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Run in test mode with the given command"
    )
    
    args = parser.parse_args()
    
    if args.test:
        run_test_mode(args.test)
    else:
        try:
            asyncio.run(run_telegram_bot())
        except KeyboardInterrupt:
            print("\nBot stopped.")


if __name__ == "__main__":
    main()
