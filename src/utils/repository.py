from abc import ABC, abstractmethod

from sqlalchemy import delete, insert, select
from sqlalchemy.orm import selectinload


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

    async def add_one(self, data: dict) -> int:
        stmt = insert(self.model).values(**data).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def del_one(self, object_id: int) -> bool:
        stmt = delete(self.model).where(self.model.id == object_id)
        result = await self.session.execute(stmt)
        deleted = result.rowcount or 0
        return deleted > 0

    async def find_one(self, object_id: int):
        stmt = select(self.model).where(self.model.id == object_id)
        res = await self.session.scalar(stmt)
        if not res:
            return res
        return res.to_read_model()

    async def find_all(self):
        stmt = select(self.model)
        res = await self.session.execute(stmt)
        res = [row[0].to_read_model() for row in res.all()]
        return res


class SqlAlchemyQuestionsRepository(SqlAlchemyRepository):
    async def find_all(self):
        stmt = select(self.model).options(selectinload(self.model.answers))
        res = await self.session.execute(stmt)
        res = [row[0].to_read_model() for row in res.all()]
        return res

    async def find_one(self, object_id: int):
        stmt = (
            select(self.model)
            .options(selectinload(self.model.answers))
            .where(self.model.id == object_id)
        )
        res = await self.session.scalar(stmt)
        if not res:
            return res
        return res.to_read_model()
