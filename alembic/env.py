from logging.config import fileConfig
from sqlalchemy import create_engine
from alembic import context
from app.core.config import settings
from app.db.session import Base

from app.models.choice import Choice
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.user import User

config = context.config
fileConfig(config.config_file_name) if config.config_file_name else None

engine = create_engine(settings.DATABASE_URL, echo=True)
target_metadata = Base.metadata

def run_migrations_offline():
    """오프라인 모드 (동기 방식)"""
    context.configure(
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """온라인 모드 (동기 방식)"""
    with engine.connect() as connection:
        context.configure(                
            connection=connection,
            target_metadata=target_metadata,
            dialect_opts={"paramstyle": "named"},
            compare_type=True,
            compare_server_default=True
        )
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
