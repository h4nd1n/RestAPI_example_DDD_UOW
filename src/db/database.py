import logging

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.core.config import DbConfig

logger = logging.getLogger(__name__)


class Database:
    def __init__(
        self,
        db_config: DbConfig | None,
        echo=True,
        pool_size=5,
        max_overflow=10,
    ):
        self.db_config = db_config
        self.engine = create_async_engine(
            url=self.db_config.database_url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.session_maker: async_sessionmaker = async_sessionmaker(self.engine)
