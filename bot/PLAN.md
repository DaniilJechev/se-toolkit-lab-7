# Development Plan: Telegram Bot for LMS Analytics

## Overview

This document outlines the development plan for the Telegram bot that provides analytics and insights from the Learning Management System (LMS). The bot will serve as an interface for students to check their scores, submissions, and get AI-powered assistance.

## Architecture

The bot follows a layered architecture with clear separation of concerns:

1. **Entry Point (bot.py)**: Handles Telegram webhook/polling and CLI test mode
2. **Handlers Layer**: Pure functions that process commands without Telegram dependencies
3. **Services Layer**: API clients for LMS backend and LLM provider
4. **Configuration**: Environment-based configuration loading

## Task Breakdown

### Task 1: Project Scaffold (Current)
- Create directory structure with handlers/, services/, config.py
- Implement --test CLI mode for offline testing
- Set up pyproject.toml with dependencies
- Create PLAN.md development roadmap

### Task 2: Core Commands Implementation
- `/start` - Welcome message with quick start guide
- `/help` - List of available commands with descriptions
- `/health` - Backend connectivity check
- `/labs` - List available labs
- `/scores [lab]` - Display scores for specific lab or all labs
- `/submissions [lab]` - Show recent submissions

### Task 3: Intent Routing with LLM
- Implement natural language understanding using LLM
- Route user queries to appropriate handlers
- Support queries like "what labs are available", "show my scores"
- Fallback to help message for unrecognized intents

### Task 4: Deployment
- Docker containerization of the bot
- Integration with existing docker-compose setup
- Health checks and restart policies
- Logging configuration

## Testing Strategy

- Unit tests for handlers (pytest)
- Integration tests with mock API responses
- CLI test mode for manual verification
- End-to-end testing via Telegram

## Dependencies

- `aiogram` or `python-telegram-bot`: Telegram Bot API
- `httpx`: Async HTTP client for API calls
- `pydantic`: Settings validation
- `typer`: CLI interface for test mode

## Timeline

1. Week 1: Scaffold + Core Commands (Tasks 1-2)
2. Week 2: Intent Routing (Task 3)
3. Week 3: Deployment + Polish (Task 4)

## Success Criteria

- All commands respond within 5 seconds
- 99% uptime on VM deployment
- Test coverage > 80%
- Clean architecture with testable components
