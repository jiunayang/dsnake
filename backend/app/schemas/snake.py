from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SnakeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    scientific_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    temperament: Optional[str] = Field(None, max_length=100)
    treatment: Optional[str] = None
    is_venomous: bool = False
    image: Optional[str] = None


class SnakeCreate(SnakeBase):
    pass


class SnakeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    scientific_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    temperament: Optional[str] = Field(None, max_length=100)
    treatment: Optional[str] = None
    is_venomous: Optional[bool] = None
    image: Optional[str] = None


class SnakeListItem(BaseModel):
    id: int
    name: str
    is_venomous: bool
    image: Optional[str] = None

    class Config:
        from_attributes = True


class SnakeDetail(BaseModel):
    id: int
    name: str
    scientific_name: Optional[str] = None
    description: Optional[str] = None
    temperament: Optional[str] = None
    treatment: Optional[str] = None
    is_venomous: bool
    image: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SnakeListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[SnakeListItem]
