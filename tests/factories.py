from datetime import datetime
from random import choice

import factory
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.tables import models

class AsyncSQLAlchemyModelFactory(factory.Factory):
    class Meta:
        abstract = True

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs):
        obj = cls.build(**kwargs)
        session.add(obj)
        await session.commit()
        return obj

class GameSessionFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = models.GameSession

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Faker('uuid4')
    platform = factory.LazyFunction(lambda: choice(("Windows", "MacOS", "Linux", "iOS", "Android")))
    session_start = factory.LazyFunction(datetime.now)
    session_end = None
    last_heartbeat = factory.LazyFunction(datetime.now)
