# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import Base  # SQLAlchemy Base 클래스
from app.db.session import get_db  # FastAPI 의존성

# 테스트용 SQLite 메모리 데이터베이스 URL
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 비동기 엔진 및 세션 설정
engine = create_async_engine(TEST_DATABASE_URL, future=True)
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 데이터베이스 세션 픽스처 정의
@pytest.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        # 모든 테이블 삭제 후 생성 (테스트 초기화)
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

# FastAPI 의존성 오버라이드 픽스처
@pytest.fixture(scope="function")
def override_get_db(db_session):
    async def _override_get_db():
        async with db_session as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db
    return _override_get_db

# TestClient 픽스처 정의
@pytest.fixture(scope="module")
def client(override_get_db):
    return TestClient(app)
