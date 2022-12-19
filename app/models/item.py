from enum import Enum
from pydantic import BaseModel, Field


class Category(str, Enum):
    CAT1 = "cat1",
    CAT2 = "cat2",
    CAT3 = "cat3"


class Item(BaseModel):
    name: str = Field(..., max_length=40)
    desc: str = Field(..., max_length=400)
    price: float = Field(..., gt=0)
    category: Category = Field(...)
    quantity: int = 0

    class Config:
        schema_extra = {
            "example": {
                "name": "item1",
                "desc": "This is the description",
                "price": 1.0,
                "category": "cat1"
            }
        }


class ItemReturn(BaseModel):
    name: str = Field(..., max_length=40)
    desc: str = Field(..., max_length=400)
    price: float = Field(..., gt=0)
    category: Category = Field(...)


class UpdateItem(BaseModel):
    name: str = Field(None, max_length=40)
    desc: str = Field(None, max_length=400)
    price: float = Field(None, gt=0)
    category: Category = Field(None)

    class Config:
        schema_extra = {
            "example": {
                "name": "item1",
                "desc": "This is the description",
                "price": 1.0,
                "category": "cat1"
            }
        }
