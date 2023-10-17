from typing import TYPE_CHECKING

from core.db.model import BaseModel
from domain.string import TableName
from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    from domain.datasource.answer import AnswerModel
    from domain.datasource.question import SuggestedQuestionModel


class UserModel(BaseModel):
    __tablename__ = TableName.user

    suggested_question_list: Mapped["SuggestedQuestionModel"] = relationship(back_populates="user")
    answer_list: Mapped["AnswerModel"] = relationship(back_populates="user")