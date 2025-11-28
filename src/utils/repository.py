from abc import ABC, abstractmethod

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from src.db.db_exceptions import map_integrity_error


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict) -> int:
        raise NotImplementedError

    @abstractmethod
    async def del_one(self, object_id: int) -> int:
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, object_id: int):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session):
        self.session = session

    # хуки
    @property
    def _get_find_one_options(self) -> tuple:
        return ()

    @property
    def _get_find_all_options(self) -> tuple:
        return ()

    # методы
    async def add_one(self, data: dict) -> int:
        try:
            obj = self.model(**data)
            self.session.add(obj)
            await self.session.flush()
            return obj.id
        except IntegrityError as e:
            raise map_integrity_error(e) from e

    async def del_one(self, object_id: int) -> bool:
        stmt = delete(self.model).where(self.model.id == object_id)
        result = await self.session.execute(stmt)
        deleted = result.rowcount or 0
        return deleted > 0

    async def find_one(self, object_id: int):
        stmt = (
            select(self.model)
            .options(*self._get_find_one_options)
            .where(self.model.id == object_id)
        )
        res = await self.session.scalar(stmt)
        if not res:
            return res
        return res.to_read_model()

    async def find_all(self):
        stmt = select(self.model).options(*self._get_find_all_options)
        res = await self.session.execute(stmt)
        return [row[0].to_read_model() for row in res.all()]


class SqlAlchemyQuestionsRepository(SqlAlchemyRepository):
    @property
    def _get_find_one_options(self) -> tuple:
        return (selectinload(self.model.answers),)

    @property
    def _get_find_all_options(self) -> tuple:
        return (selectinload(self.model.answers),)
