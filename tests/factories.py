from datetime import datetime
from random import choice

import factory
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.tables import models
from app.database.tables.models import GameSession, User
from app.core.password_utils import get_password_hash


class AsyncSQLAlchemyModelFactory(factory.Factory):
    class Meta:
        abstract = True

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> GameSession:
        obj = cls.build(**kwargs)
        session.add(obj)
        await session.commit()
        return obj

class GameSessionFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = models.GameSession

    user_id = factory.Faker('uuid4')
    platform = factory.LazyFunction(lambda: choice(("Windows", "MacOS", "Linux", "iOS", "Android")))
    session_start = factory.LazyFunction(datetime.now)
    session_end = None
    last_heartbeat = factory.LazyFunction(datetime.now)


TEST_PASSWORD = 'password123'


class UserFactory(AsyncSQLAlchemyModelFactory):


    class Meta:
        model = User

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    hashed_password = factory.LazyAttribute(lambda _: get_password_hash(TEST_PASSWORD))
    is_active = True
    full_name = factory.Faker("name")
