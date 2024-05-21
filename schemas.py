from pydantic import BaseModel, Field


class ThemeApp(BaseModel):
    name: str
    description: str


class ThemeAppResponse(BaseModel):
    id: int = Field(gt=0)
    name: str
    description: str


class CommentApp(BaseModel):
    author_name: str
    text: str
    quote_id: int = -1


class CommentAppResponse(BaseModel):
    id: int
    theme_id: int
    author_id: int
    author_name: str
    text: str
    quote_id: int


class GetThemesResponse(BaseModel):
    id: int
    name: str
    description: str


class ThemeCommentsResponse(BaseModel):
    id: int
    theme_id: int
    author_name: str
    text: str
    quote_id: int = -1


class EditComment(BaseModel):
    author_name: str
    text: str
    quote_id: int | None = -1
