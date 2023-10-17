from typing import List

from api.exception import UnprocessableEntity
from api.router.answer.request import AddAnswerRequest
from api.router.answer.response import AnswerResponse
from api.router.answer.string import AnswerEndPoint
from api.util import get_current_user
from core.db.session import get_session
from domain.repository.answer import AnswerRepository
from domain.repository.question import QuestionRepository
from domain.service.answer import AnswerService
from domain.service.question import QuestionService
from domain.service.user import UserSchema
from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

answer_router = APIRouter()


@answer_router.get(path=AnswerEndPoint.list)
async def list(
    question_id: UUID4,
    limit: int = 20,
    offset: int = 0,
    user: UserSchema = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> List[AnswerResponse]:
    answer_repository = AnswerRepository(
        session=session,
    )
    answer_service = AnswerService(
        answer_repository=answer_repository,
    )
    answer_list = await answer_service.list(
        question_external_id=str(question_id),
        user_id=user.id,
        limit=limit,
        offset=offset,
    )
    return [
        AnswerResponse(
            external_id=answer.external_id,
            answer=answer.answer,
        )
        for answer in answer_list
    ]


@answer_router.post(path=AnswerEndPoint.add)
async def add(
    question_id: UUID4,
    request: AddAnswerRequest,
    user: UserSchema = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    question_repository = QuestionRepository(
        session=session,
    )
    answer_repository = AnswerRepository(
        session=session,
    )
    question_service = QuestionService(
        question_repository=question_repository,
    )
    answer_service = AnswerService(
        answer_repository=answer_repository,
    )

    internal_question_schema = await question_service.find_first_by_external_id(
        external_id=str(question_id),
    )

    if not internal_question_schema:
        raise UnprocessableEntity

    await answer_service.add(
        user_id=user.id,
        question_id=internal_question_schema.id,
        answer=request.answer,
    )

    await session.commit()
