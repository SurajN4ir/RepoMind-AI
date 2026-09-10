from collections.abc import AsyncGenerator

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config.settings import Settings
from app.main import create_app
from app.shared.database.session import build_async_engine, get_db_session


def test_health_check_returns_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"]


def test_readiness_check_returns_ok_when_database_reachable() -> None:
    # Overrides get_db_session with an isolated in-memory SQLite session so this
    # test doesn't depend on a real PostgreSQL instance being reachable -- it's
    # only proving the endpoint's connectivity check itself, not any one backend.
    engine = build_async_engine(Settings(database_url="sqlite+aiosqlite:///:memory:"))
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def fake_get_db_session() -> AsyncGenerator[AsyncSession]:
        async with factory() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_db_session] = fake_get_db_session
    client = TestClient(app)

    response = client.get("/api/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
