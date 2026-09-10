"""Shared pytest configuration."""

import asyncio
import sys

if sys.platform == "win32":
    # psycopg's async driver cannot run on Windows's default ProactorEventLoop;
    # it requires a SelectorEventLoop. Only affects real PostgreSQL connections
    # (e.g. test_pgvector_repository.py) -- aiosqlite is unaffected either way.
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
