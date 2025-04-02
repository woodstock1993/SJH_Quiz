from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from app.core.config import settings
from app.models.user import User
import asyncio

config = context.config
fileConfig(config.config_file_name) if config.config_file_name else None

engine = create_async_engine(settings.DATABASE_URL, echo=True)
target_metadata = User.metadata

def run_migrations_offline():
    """오프라인 모드 (동기 방식)"""
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """온라인 모드 (비동기 방식)"""
    async with engine.connect() as connection:
        # 1. 컨텍스트에 연결 및 메타데이터 설정
        def run_migrations(conn):
            context.configure(
                connection=conn, 
                target_metadata=target_metadata
            )
            with context.begin_transaction():
                context.run_migrations()

        # 2. 동기 함수를 비동기로 실행
        await connection.run_sync(run_migrations)

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
