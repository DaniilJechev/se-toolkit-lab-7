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


def parse_command(text: str) -> tuple[str, Optional[str]]:
    """
    Parse command text into command name and argument.
    
    Args:
        text: Input text (e.g., "/scores lab-04" or "what labs are available")
    
    Returns:
        Tuple of (command, argument)
    """
    text = text.strip()
    
    # Handle slash commands
    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        command = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else None
        return command, arg
    
    # Handle natural language - will be processed by intent router
    return text.lower(), None


def route_command(command: str, arg: Optional[str] = None) -> str:
    """
    Route command to appropriate handler.
    
    Args:
        command: Command name (without /)
        arg: Optional command argument
    
    Returns:
        Handler response string
    """
    command = command.lower().lstrip("/")
    
    if command == "start":
        return handle_start()
    elif command == "help":
        return handle_help()
    elif command == "health":
        return handle_health()
    elif command == "labs":
        return handle_labs()
    elif command == "scores":
        return handle_scores(arg)
    elif command == "submissions":
        return handle_submissions(arg)
    else:
        return handle_unknown(command)


async def process_message_async(text: str) -> str:
    """
    Process message with potential async operations (LLM, API).
    
    Args:
        text: User message text
    
    Returns:
        Response string
    """
    command, arg = parse_command(text)
    
    # For now, use simple routing
    # Task 3 will add LLM-based intent classification
    return route_command(command, arg)


def run_test_mode(command: str) -> None:
    """
    Run bot in test mode - process command and print result.
    
    Args:
        command: Command to test (e.g., "/start", "/help")
    """
    import asyncio
    
    async def run():
        response = await process_message_async(command)
        print(response)
        return 0
    
    exit_code = asyncio.run(run())
    sys.exit(exit_code)


async def run_telegram_bot() -> None:
    """Run the bot with Telegram polling."""
    try:
        from aiogram import Bot, Dispatcher, types
        from aiogram.filters import CommandStart
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
        await message.answer(handle_health())
    
    @dp.message(Command("labs"))
    async def on_labs(message: types.Message):
        await message.answer(handle_labs())
    
    @dp.message(Command("scores"))
    async def on_scores(message: types.Message):
        lab_name = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        await message.answer(handle_scores(lab_name))
    
    @dp.message(Command("submissions"))
    async def on_submissions(message: types.Message):
        lab_name = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        await message.answer(handle_submissions(lab_name))
    
    @dp.message()
    async def on_message(message: types.Message):
        # Task 3: Add LLM intent routing here
        await message.answer(handle_unknown(message.text))
    
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
        import asyncio
        try:
            asyncio.run(run_telegram_bot())
        except KeyboardInterrupt:
            print("\nBot stopped.")


if __name__ == "__main__":
    main()
