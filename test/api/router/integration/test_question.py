from http import HTTPStatus

from assertpy import assert_that
from core.config import get_config
from core.util.jwt import JWTUtil
from domain.datasource.answer import AnswerModel
from domain.repository.question import QuestionModel, SuggestedQuestionModel
from domain.repository.user import UserModel
from domain.service.jwt import JWTSchema, JWTService
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


async def test_recommendation_list_order_by_suggested_count_asc(
    client: AsyncClient, session: AsyncSession, user_model: UserModel, jwt_schema: JWTSchema
):
    question_model1 = QuestionModel()
    question_model2 = QuestionModel()
    question_model3 = QuestionModel()
    session.add_all(
        instances=[
            question_model1,
            question_model2,
            question_model3,
        ]
    )
    await session.commit()
    session.add_all(
        instances=[
            SuggestedQuestionModel(question_id=question_model1.id, user_id=user_model.id),
            SuggestedQuestionModel(question_id=question_model1.id, user_id=user_model.id),
            SuggestedQuestionModel(question_id=question_model2.id, user_id=user_model.id),
        ]
    )
    await session.commit()

    response = await client.get(
        url="/question/recommendation",
        headers={
            "Authorization": f"JWT {jwt_schema.access_token}",
        },
    )

    assert_that(response.status_code).is_equal_to(HTTPStatus.OK)
    response_data = response.json()
    assert_that(response_data[0]["id"]).is_equal_to(str(question_model3.external_id))
    assert_that(response_data[1]["id"]).is_equal_to(str(question_model2.external_id))
    assert_that(response_data[2]["id"]).is_equal_to(str(question_model1.external_id))


async def test_recommendation_list_rotation(
    client: AsyncClient, session: AsyncSession, user_model: UserModel, jwt_schema: JWTSchema
):
    question_model1 = QuestionModel()
    question_model2 = QuestionModel()
    question_model3 = QuestionModel()
    question_model4 = QuestionModel()
    question_model5 = QuestionModel()
    question_model6 = QuestionModel()
    session.add_all(
        instances=[
            question_model1,
            question_model2,
            question_model3,
            question_model4,
            question_model5,
            question_model6,
        ]
    )
    await session.commit()

    response = await client.get(
        url="/question/recommendation",
        headers={
            "Authorization": f"JWT {jwt_schema.access_token}",
        },
    )

    assert_that(response.status_code).is_equal_to(HTTPStatus.OK)
    response_data = response.json()
    assert_that(response_data[0]["id"]).is_equal_to(str(question_model1.external_id))
    assert_that(response_data[1]["id"]).is_equal_to(str(question_model2.external_id))
    assert_that(response_data[2]["id"]).is_equal_to(str(question_model3.external_id))

    response = await client.get(
        url="/question/recommendation",
        headers={
            "Authorization": f"JWT {jwt_schema.access_token}",
        },
    )

    assert_that(response.status_code).is_equal_to(HTTPStatus.OK)
    response_data = response.json()
    assert_that(response_data[0]["id"]).is_equal_to(str(question_model4.external_id))
    assert_that(response_data[1]["id"]).is_equal_to(str(question_model5.external_id))
    assert_that(response_data[2]["id"]).is_equal_to(str(question_model6.external_id))

    response = await client.get(
        url="/question/recommendation",
        headers={
            "Authorization": f"JWT {jwt_schema.access_token}",
        },
    )

    assert_that(response.status_code).is_equal_to(HTTPStatus.OK)
    response_data = response.json()
    assert_that(response_data[0]["id"]).is_equal_to(str(question_model1.external_id))
    assert_that(response_data[1]["id"]).is_equal_to(str(question_model2.external_id))
    assert_that(response_data[2]["id"]).is_equal_to(str(question_model3.external_id))


async def test_answered_question_list(
    client: AsyncClient, session: AsyncSession, user_model: UserModel, jwt_schema: JWTSchema
):
    question_model1 = QuestionModel()
    question_model2 = QuestionModel()
    question_model3 = QuestionModel()
    question_model4 = QuestionModel()
    question_model5 = QuestionModel()
    question_model6 = QuestionModel()
    session.add_all(
        instances=[
            question_model1,
            question_model2,
            question_model3,
            question_model4,
            question_model5,
            question_model6,
        ]
    )
    await session.commit()
    answer_model1 = AnswerModel(
        question=question_model1,
        user=user_model,
    )
    answer_model2 = AnswerModel(
        question=question_model2,
        user=user_model,
    )
    answer_model3 = AnswerModel(
        question=question_model3,
        user=user_model,
    )
    session.add_all(
        instances=[
            answer_model1,
            answer_model2,
            answer_model3,
        ]
    )
    await session.commit()

    response = await client.get(
        url="/question/answered?limit=2&offset=0",
        headers={
            "Authorization": f"JWT {jwt_schema.access_token}",
        },
    )
    assert_that(response.status_code).is_equal_to(HTTPStatus.OK)
    response_data = response.json()

    assert_that(response_data[0]["id"]).is_equal_to(str(question_model1.external_id))
    assert_that(response_data[1]["id"]).is_equal_to(str(question_model2.external_id))

    response = await client.get(
        url="/question/answered?limit=2&offset=2",
        headers={
            "Authorization": f"JWT {jwt_schema.access_token}",
        },
    )
    assert_that(response.status_code).is_equal_to(HTTPStatus.OK)
    response_data = response.json()

    assert_that(response_data).is_length(1)
    assert_that(response_data[0]["id"]).is_equal_to(str(question_model3.external_id))

    response = await client.get(
        url="/question/answered?limit=2&offset=4",
        headers={
            "Authorization": f"JWT {jwt_schema.access_token}",
        },
    )
    assert_that(response.status_code).is_equal_to(HTTPStatus.OK)
    response_data = response.json()

    assert_that(response_data).is_empty()


async def test_answered_question_list_only_given_user(
    client: AsyncClient, session: AsyncSession, user_model: UserModel, jwt_schema: JWTSchema
):
    question_model1 = QuestionModel()
    user_model2 = UserModel()
    question_model2 = QuestionModel()
    session.add_all(
        instances=[
            question_model1,
            user_model2,
            question_model2,
        ]
    )
    await session.commit()
    answer_model1 = AnswerModel(
        question=question_model1,
        user=user_model,
    )
    answer_model2 = AnswerModel(
        question=question_model2,
        user=user_model2,
    )
    session.add_all(
        instances=[
            answer_model1,
            answer_model2,
        ]
    )
    await session.commit()

    response = await client.get(
        url="/question/answered",
        headers={
            "Authorization": f"JWT {jwt_schema.access_token}",
        },
    )
    assert_that(response.status_code).is_equal_to(HTTPStatus.OK)
    response_data = response.json()

    assert_that(response_data).is_length(1)
    assert_that(response_data[0]["id"]).is_equal_to(str(question_model1.external_id))
