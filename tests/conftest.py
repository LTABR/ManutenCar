"""Configuração dos testes: SQLite em memória e cliente FastAPI."""

from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models import User
from app.security import create_access_token, hash_password


@pytest.fixture
def client_and_session() -> Generator[tuple[TestClient, sessionmaker], None, None]:
    """Cria um banco SQLite compartilhado e sobrescreve a dependência get_db.

    O TestClient é criado sem o bloco ``with`` para não disparar o startup
    da aplicação, que tentaria conectar ao MySQL configurado no .env.
    """

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    try:
        yield client, testing_session
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def create_user(session_factory: sessionmaker, email: str) -> tuple[str, str]:
    """Insere um usuário e retorna ``(id, token JWT)``."""

    db = session_factory()
    try:
        user = User(
            id=str(uuid4()),
            email=email,
            password_hash=hash_password("test-password"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user.id, create_access_token(user.id)
    finally:
        db.close()


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
