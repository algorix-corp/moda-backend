from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4


class User(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    phone_number: str
    username: str
    card_number: str
