import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# -------------------------------------------------------------------
# ✅ FINAL FIX — make sure Alembic always finds your "app" package
# -------------------------------------------------------------------
import importlib.util

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
APP_DIR = os.path.join(BACKEND_DIR, "app")

# Add both backend/ and backend/app to sys.path
for path in [BACKEND_DIR, APP_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

print("📦 CURRENT_DIR:", CURRENT_DIR)
print("📦 BACKEND_DIR:", BACKEND_DIR)
print("📦 APP_DIR:", APP_DIR)
print("📦 sys.path (first 3):", sys.path[:3])
print("📂 session.py exists?:", os.path.exists(os.path.join(APP_DIR, "db", "session.py")))

# ✅ Imports
from app.db.base import Base
from app.db.models import *  # noqa
from app.db.session import engine


# -------------------------------------------------------------------
# Alembic configuration
# -------------------------------------------------------------------
config = context.config

# Set up Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ Link Alembic to your SQLAlchemy models
target_metadata = Base.metadata

# -------------------------------------------------------------------
# Helper functions to run migrations
# -------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# -------------------------------------------------------------------
# Entry point
# -------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
