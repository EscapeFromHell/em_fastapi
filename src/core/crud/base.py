from typing import Generic, Type, TypeVar

from pydantic import BaseModel

from src.core.models import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        Initialize the CRUDBase class.

        :param model: Type[ModelType] - SQLAlchemy model type.
        """
        self.model = model
