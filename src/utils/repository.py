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

    def __init__(self, session_maker):
        self.session_maker = session_maker

    async def add_one(self, data: dict) -> int:
        async with self.session_maker() as session:
            async with session.begin():
                stmt = insert(self.model).values(**data).returning(self.model.id)
                res = await session.execute(stmt)
                await session.commit()
                return res.scalar_one()

    async def del_one(self, object_id: int) -> bool:
        async with self.session_maker() as session:
            async with session.begin():
                stmt = delete(self.model).where(self.model.id == object_id)
                result = await session.execute(stmt)
                deleted = result.rowcount or 0
                return deleted > 0

    async def find_one(self, object_id: int):
        async with self.session_maker() as session:
            stmt = select(self.model).where(self.model.id == object_id)
            res = await session.scalar(stmt)
            if not res:
                return res
            return res.to_read_model()

    async def find_all(self):
        async with self.session_maker() as session:
            stmt = select(self.model)
            res = await session.execute(stmt)
            res = [row[0].to_read_model() for row in res.all()]
            return res


class SqlAlchemyQuestionsRepository(SqlAlchemyRepository):
    async def find_all(self):
        async with self.session_maker() as session:
            stmt = select(self.model).options(selectinload(self.model.answers))
            res = await session.execute(stmt)
            res = [row[0].to_read_model() for row in res.all()]
            return res

    async def find_one(self, object_id: int):
        async with self.session_maker() as session:
            stmt = (
                select(self.model)
                .options(selectinload(self.model.answers))
                .where(self.model.id == object_id)
            )
            res = await session.scalar(stmt)
            if not res:
                return res
            return res.to_read_model()
