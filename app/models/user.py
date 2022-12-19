from pydantic import BaseModel, Field


class User(BaseModel):
    first: str = Field(..., max_length=40)
    last: str = Field(..., max_length=40)
    cart: list[dict] = []

    class Config:
        schema_extra = {
            "example": {
                "first": "Rychu",
                "last": "Gryps"
            }
        }


class UpdateUser(BaseModel):
    first: str = Field(None, max_length=40)
    last: str = Field(None, max_length=40)

    class Config:
        schema_extra = {
            "example": {
                "first": "Rychu",
                "last": "Gryps",
            }
        }



