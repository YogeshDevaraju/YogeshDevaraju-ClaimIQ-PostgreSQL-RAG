from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from src.core.config import settings
from src.db.base import Base

from src.models.audit_log import AuditLog
from src.models.chat_query_log import ChatQueryLog
from src.models.claim import Claim
from src.models.claim_note import ClaimNote
from src.models.claim_status_history import ClaimStatusHistory
from src.models.document import Document
from src.models.document_chunk import DocumentChunk
from src.models.policy import Policy
from src.models.user import User


config = context.config

config.set_main_option(
    "sqlalchemy.url",
    settings.database_url,
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


def include_object(
    object_,
    name,
    type_,
    reflected,
    compare_to,
):
    if type_ == "table" and name == "entity_history":
        return False

    return True


def run_migrations_offline():
    database_url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        compare_type=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    configuration = config.get_section(
        config.config_ini_section,
        {},
    )

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
