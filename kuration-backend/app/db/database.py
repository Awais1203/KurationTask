"""Database"""

import enum
from asyncio import current_task
from time import perf_counter

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app import settings


class DBHost(str, enum.Enum):
    LEADER = "leader"
    FOLLOWER = "follower"


# Create async engines for leader and follower
leader_engine = create_async_engine(
    settings.LIVE_DATABASE_LEADER_URI,
    **settings.db_settings.leader.engine_options,
)
follower_engine = create_async_engine(
    settings.LIVE_DATABASE_FOLLOWER_URI,
    **settings.db_settings.follower.engine_options,
)

# Common session parameters
common_session_params = {
    "autocommit": False,
    "autoflush": False,
    "expire_on_commit": False,
}


def get_sessionmaker(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, **common_session_params)


def _get_current_task_id() -> int:
    return id(current_task())


# Create sessionmakers for leader and follower
sessionmakers = {
    DBHost.LEADER: get_sessionmaker(leader_engine),
    DBHost.FOLLOWER: get_sessionmaker(follower_engine),
}


class DBManager:
    def __init__(self, host: DBHost = DBHost.LEADER):
        self.host = host
        self.scoped_session = async_scoped_session(
            session_factory=sessionmakers[host],
            scopefunc=_get_current_task_id,
        )

    def get_session(self) -> AsyncSession:
        return self.scoped_session()


# Apply event listeners to the synchronous engine
@event.listens_for(leader_engine.sync_engine, "before_cursor_execute")
def bef_exc(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault("query_start_time", []).append(perf_counter())


@event.listens_for(leader_engine.sync_engine, "after_cursor_execute")
def post_exc(conn, cursor, statement, parameters, context, executemany):
    total = perf_counter() - conn.info["query_start_time"].pop(-1)
    print(
        f"execution time: {total}; parameters: {parameters}; statement: {statement}"
    )


# Base class for DB models
Base = declarative_base()
