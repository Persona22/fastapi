from datetime import datetime
from uuid import uuid4

from assertpy import assert_that
from domain.datasource.user import UserModel
from domain.repository.user import UserRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session


async def test_find_first_by_external_id(session: AsyncSession):
    user_repository = UserRepository(session=session)
    user_model = UserModel()
    session.add(instance=user_model)
    await session.commit()

    user_result = await user_repository.find_first_by_external_id(external_id=user_model.external_id)
    assert_that(user_result).is_not_none()


async def test_find_first_by_external_id_exclude_deleted_data(session: AsyncSession):
    user_repository = UserRepository(session=session)
    user_model = UserModel(delete_datetime=datetime.now())
    session.add(instance=user_model)
    await session.commit()

    user_result = await user_repository.find_first_by_external_id(
        external_id=user_model.external_id,
    )
    assert_that(user_result).is_none()


async def test_find_first_by_external_id_return_none_when_not_exist(session: AsyncSession):
    user_repository = UserRepository(session=session)

    user_result = await user_repository.find_first_by_external_id(external_id=str(uuid4()))
    assert_that(user_result).is_none()


async def test_register(session: AsyncSession):
    user_repository = UserRepository(session=session)

    user_model = await user_repository.register()
    await session.commit()

    result = await session.scalar(select(UserModel))

    assert_that(user_model).is_not_none()
    assert_that(user_model.external_id).is_equal_to(result.external_id)


async def test_delete(session: AsyncSession):
    user_repository = UserRepository(session=session)
    user_model = UserModel()
    session.add(
        instance=user_model,
    )
    await session.commit()
    await user_repository.delete(
        user_model=user_model
    )
    await session.commit()

    result = await session.scalar(select(UserModel).where(UserModel.id == user_model.id))

    assert_that(result).is_not_none()
    assert_that(result.delete_datetime).is_not_none()
