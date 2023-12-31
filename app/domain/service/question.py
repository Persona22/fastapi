from datetime import datetime

from core.language import SupportLanguage
from domain.repository.question import QuestionRepository
from domain.service.base import BaseService
from pydantic import UUID4, BaseModel


class QuestionSchema(BaseModel):
    external_id: UUID4
    question: str


class InternalQuestionSchema(BaseModel):
    id: int


class AnsweredQuestionSchema(BaseModel):
    id: UUID4
    question: str
    answer_count: int
    answer_datetime: datetime


class QuestionService(BaseService):
    def __init__(self, question_repository: QuestionRepository):
        self._question_repository = question_repository

    async def find_first_by_external_id(self, external_id: str) -> InternalQuestionSchema | None:
        question_model = await self._question_repository.find_first_by_external_id(external_id=external_id)
        if not question_model:
            return None

        return InternalQuestionSchema(
            id=question_model.id,
        )

    async def answered_list(
        self,
            user_id: int,
            language_code: SupportLanguage,
            start_datetime: datetime,
            end_datetime: datetime,
            limit: int,
            offset: int,
    ) -> list[AnsweredQuestionSchema]:
        question_list = await self._question_repository.answered_list(
            user_id=user_id,
            language_code=language_code,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            limit=limit,
            offset=offset,
        )

        return [
            AnsweredQuestionSchema(
                id=question.external_id,
                question=question.question,
                answer_count=question.answer_count,
                answer_datetime=question.answer_datetime,
            )
            for question in question_list
        ]

    async def recommendation_list(self, language_code: SupportLanguage, offset: int) -> list[QuestionSchema]:
        question_list = await self._question_repository.recommendation_list(
            language_code=language_code,
            limit=3,
            offset=offset,
        )

        return [
            QuestionSchema(
                external_id=str(question.external_id),
                question=question.question,
            )
            for question in question_list
        ]
