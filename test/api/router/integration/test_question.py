from datetime import datetime, timedelta
from http import HTTPStatus

from assertpy import assert_that
from core.language import SupportLanguage
from domain.datasource.answer import AnswerModel
from domain.datasource.language import LanguageModel
from domain.datasource.question import QuestionTranslationModel
from domain.repository.question import QuestionModel
from domain.repository.user import UserModel
from domain.service.jwt import JWTSchema
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


async def test_recommendation_list_order_by_answer_count_desc(
    client: AsyncClient, session: AsyncSession, jwt_schema: JWTSchema
):
    question_model1 = QuestionModel()
    question_model2 = QuestionModel(answer_count=1)
    question_model3 = QuestionModel(answer_count=2)
    language_model = LanguageModel(
        code=SupportLanguage.en.value,
    )
    session.add_all(
        instances=[
            question_model1,
            question_model2,
            question_model3,
            language_model,
        ]
    )
    await session.commit()
    session.add_all(
        instances=[
            QuestionTranslationModel(
                language=language_model,
                question=question_model1,
                text="",
            ),
            QuestionTranslationModel(
                language=language_model,
                question=question_model2,
                text="",
            ),
            QuestionTranslationModel(
                language=language_model,
                question=question_model3,
                text="",
            ),
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


async def test_answered_question_list(
    client: AsyncClient, session: AsyncSession, user_model: UserModel, jwt_schema: JWTSchema
):
    question_model1 = QuestionModel()
    question_model2 = QuestionModel()
    question_model3 = QuestionModel()
    language_model = LanguageModel(
        code=SupportLanguage.en.value,
    )
    session.add_all(
        instances=[
            question_model1,
            question_model2,
            question_model3,
            language_model,
        ]
    )
    await session.commit()

    answer_model1 = AnswerModel(
        question=question_model1,
        user=user_model,
        answer="",
    )
    answer_model2 = AnswerModel(
        question=question_model2,
        user=user_model,
        answer="",
    )
    answer_model3 = AnswerModel(
        question=question_model3,
        user=user_model,
        answer="",
    )
    session.add_all(
        instances=[
            answer_model1,
            answer_model2,
            answer_model3,
            QuestionTranslationModel(
                language=language_model,
                question=question_model1,
                text="",
            ),
            QuestionTranslationModel(
                language=language_model,
                question=question_model2,
                text="",
            ),
            QuestionTranslationModel(
                language=language_model,
                question=question_model3,
                text="",
            ),
        ]
    )
    await session.commit()

    response = await client.get(
        url=f"/question/answered?limit=2&offset=0&start_datetime={answer_model1.create_datetime}&end_datetime={answer_model3.create_datetime}",
        headers={
            "Authorization": f"JWT {jwt_schema.access_token}",
        },
    )
    assert_that(response.status_code).is_equal_to(HTTPStatus.OK)
    response_data = response.json()

    assert_that(response_data[0]["id"]).is_equal_to(str(question_model3.external_id))
    assert_that(response_data[0]["answer_count"]).is_equal_to(1)
    assert_that(response_data[0]["answer_datetime"]).is_equal_to(answer_model3.create_datetime.isoformat())
    assert_that(response_data[1]["id"]).is_equal_to(str(question_model2.external_id))
    assert_that(response_data[1]["answer_count"]).is_equal_to(1)
    assert_that(response_data[1]["answer_datetime"]).is_equal_to(answer_model2.create_datetime.isoformat())

    response = await client.get(
        url=f"/question/answered?limit=2&offset=2&start_datetime={answer_model1.create_datetime}&end_datetime={answer_model3.create_datetime}",
        headers={
            "Authorization": f"JWT {jwt_schema.access_token}",
        },
    )
    assert_that(response.status_code).is_equal_to(HTTPStatus.OK)
    response_data = response.json()

    assert_that(response_data).is_length(1)
    assert_that(response_data[0]["id"]).is_equal_to(str(question_model1.external_id))
    assert_that(response_data[0]["answer_count"]).is_equal_to(1)
    assert_that(response_data[0]["answer_datetime"]).is_equal_to(answer_model1.create_datetime.isoformat())

    response = await client.get(
        url=f"/question/answered?limit=2&offset=4&start_datetime={answer_model1.create_datetime}&end_datetime={answer_model3.create_datetime}",
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
        answer="",
    )
    answer_model2 = AnswerModel(
        question=question_model2,
        user=user_model2,
        answer="",
    )
    language_model = LanguageModel(
        code=SupportLanguage.en.value,
    )
    session.add_all(
        instances=[
            answer_model1,
            answer_model2,
            QuestionTranslationModel(
                language=language_model,
                question=question_model1,
                text="",
            ),
            QuestionTranslationModel(
                language=language_model,
                question=question_model2,
                text="",
            ),
        ]
    )
    await session.commit()

    response = await client.get(
        url=f"/question/answered?start_datetime={answer_model1.create_datetime}&end_datetime={answer_model2.create_datetime}",
        headers={
            "Authorization": f"JWT {jwt_schema.access_token}",
        },
    )
    assert_that(response.status_code).is_equal_to(HTTPStatus.OK)
    response_data = response.json()

    assert_that(response_data).is_length(1)
    assert_that(response_data[0]["id"]).is_equal_to(str(question_model1.external_id))


async def test_unprocessable_entity_answered_question_list_over_31_day(
    client: AsyncClient, jwt_schema: JWTSchema,
):
    now = datetime.now()
    next_32_day = now + timedelta(days=32)
    response = await client.get(
        url=f"/question/answered?start_datetime={now}&end_datetime={next_32_day}",
        headers={
            "Authorization": f"JWT {jwt_schema.access_token}",
        },
    )
    assert_that(response.status_code).is_equal_to(HTTPStatus.UNPROCESSABLE_ENTITY)
