"""
Pytest configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from main import app

# Import all models to ensure they're registered with Base
from app.models import Account, Transaction, User  # noqa: F401

# Use in-memory SQLite database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with the test database."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_accounts(db_session):
    """Create sample accounts for testing transfers."""
    from app.models import Account

    source = Account(
        account_number="ACC-SOURCE-001",
        account_holder="John Doe",
        account_type="checking",
        balance=10000.0,
    )
    destination = Account(
        account_number="ACC-DEST-002",
        account_holder="Jane Smith",
        account_type="savings",
        balance=5000.0,
    )

    db_session.add(source)
    db_session.add(destination)
    db_session.commit()
    db_session.refresh(source)
    db_session.refresh(destination)

    return source, destination


@pytest.fixture
def auth_headers(db_session):
    """Create authentication headers for testing."""
    from app.models.user import User
    from app.services.auth_service import AuthService
    from app.repositories.user_repository import UserRepository
    import uuid

    # Create a test user with explicit ID
    user = User(
        id=str(uuid.uuid4()),
        username="testuser",
        email="test@example.com",
        hashed_password="$2b$12$KIXVZj5Z7Z8Z8Z8Z8Z8Z8.Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8",  # "password"
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    # Create auth token
    auth_service = AuthService(UserRepository(db_session))
    token = auth_service.create_access_token(data={"sub": user.username})

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def db(db_session):
    """Alias for db_session to match test expectations."""
    return db_session
