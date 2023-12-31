from typing import List

from api.depdendency import get_answer_service, get_question_service
from api.exception import UnprocessableEntity
from api.router.answer.request import AddAnswerRequest, EditAnswerRequest
from api.router.answer.response import AnswerResponse
from api.router.answer.string import AnswerDetailEndPoint, AnswerEndPoint
from api.util.auth import get_current_user
from core.db.session import get_session
from domain.service.answer import AnswerService
from domain.service.exception import DoesNotExist
from domain.service.question import QuestionService
from domain.service.user import InternalUserSchema
from fastapi import APIRouter, Depends, Query
from pydantic import UUID4
from result import Err
from sqlalchemy.ext.asyncio import AsyncSession

answer_detail_router = APIRouter()
answer_router = APIRouter()


@answer_router.get(path=AnswerEndPoint.list)
async def _list(
    question_id: UUID4,
    limit: int = Query(default=20, lt=21),
    offset: int = 0,
    user: InternalUserSchema = Depends(get_current_user),
    answer_service: AnswerService = Depends(get_answer_service),
) -> List[AnswerResponse]:
    answer_list = await answer_service.list(
        question_external_id=str(question_id),
        user_id=user.id,
        limit=limit,
        offset=offset,
    )
    return [
        AnswerResponse(
            id=answer.external_id,
            answer=answer.answer,
            create_datetime=answer.create_datetime,
        )
        for answer in answer_list
    ]


@answer_router.post(path=AnswerEndPoint.add)
async def add(
    question_id: UUID4,
    request: AddAnswerRequest,
    user: InternalUserSchema = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    answer_service: AnswerService = Depends(get_answer_service),
    question_service: QuestionService = Depends(get_question_service),
) -> None:
    question_schema = await question_service.find_first_by_external_id(external_id=str(question_id))
    if not question_schema:
        raise UnprocessableEntity

    await answer_service.add(
        user_id=user.id,
        question_id=question_schema.id,
        answer=request.answer,
    )

    await session.commit()


@answer_detail_router.patch(path=AnswerDetailEndPoint.edit)
async def edit(
    answer_id: UUID4,
    request: EditAnswerRequest,
    user: InternalUserSchema = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    answer_service: AnswerService = Depends(get_answer_service),
) -> None:
    result = await answer_service.edit(
        answer_external_id=str(answer_id),
        user_id=user.id,
        answer=request.answer,
    )

    match result:
        case Err(exception):
            match exception:
                case DoesNotExist():
                    raise UnprocessableEntity

    await session.commit()


@answer_detail_router.delete(path=AnswerDetailEndPoint.delete)
async def delete(
    answer_id: UUID4,
    user: InternalUserSchema = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    answer_service: AnswerService = Depends(get_answer_service),
) -> None:
    result = await answer_service.delete(
        answer_external_id=str(answer_id),
        user_id=user.id,
    )

    match result:
        case Err(exception):
            match exception:
                case DoesNotExist():
                    raise UnprocessableEntity

    await session.commit()
