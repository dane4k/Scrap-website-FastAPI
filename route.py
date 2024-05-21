from typing import List
from fastapi import FastAPI
import random as rd
from schemas import *
from crud import *
from sqlalchemy.orm import sessionmaker

session = sessionmaker(bind=engine)()

app = FastAPI(title='Форум "Криминалист"')


@app.post("/theme/", response_model=ThemeAppResponse)
def create_theme(theme: ThemeApp):
    new_id = rd.randint(500, 100000)
    new_theme = Theme(id_=new_id, name=theme.name, text=theme.description)
    add_object(new_theme, session)
    return ThemeAppResponse(id=new_theme.id_, name=new_theme.name, description=new_theme.text)


@app.post("/comment/{theme_id}")
def create_comment(theme_id: int, comment: CommentApp):
    id_ = rd.randint(500, 100000)
    author_id = rd.randint(500, 100000)
    new_comment = Comment(id_=id_, theme_id=theme_id, author_id=author_id, author_name=comment.author_name,
                          text=comment.text, quote_id=comment.quote_id)
    add_object(new_comment, session)
    return [CommentAppResponse(id=new_comment.id_, theme_id=new_comment.theme_id, author_id=new_comment.author_id,
                               author_name=new_comment.author_name,
                               text=new_comment.text, quote_id=new_comment.quote_id)]


@app.get("/themes", response_model=List[GetThemesResponse])
def get_themes():
    themes_data = get_objects(Theme, session)
    return [GetThemesResponse(id=theme.id_, name=theme.name, description=theme.text) for theme in themes_data]


@app.get("/theme/{theme_id}", response_model=List[GetThemesResponse])
def get_theme(theme_id: int):
    requested_theme = get_object(Theme, theme_id, session)
    return [GetThemesResponse(id=requested_theme.id_, name=requested_theme.name, description=requested_theme.text)]


@app.get("/comment/{theme_id}/comments")
def get_theme_comments(theme_id: int):
    requested_comments = get_comments_by_theme_id(theme_id, session)
    return [
        ThemeCommentsResponse(id=comment.id_, theme_id=comment.theme_id, author_name=comment.author_name,
                              text=comment.text)
        for comment in requested_comments]


@app.get("/comment/{comment_id}/details")
def get_comment(comment_id: int):
    requested_comment = get_object(Comment, comment_id, session)
    return ThemeCommentsResponse(id=requested_comment.id_, theme_id=requested_comment.theme_id,
                                 author_name=requested_comment.author_name, text=requested_comment.text)


@app.put("/comment/{comment_id}/edit", response_model=ThemeCommentsResponse)
def edit_comment(comment_id: int, comment: EditComment):
    new_comment = EditComment(author_name=comment.author_name, text=comment.text, quote_id=comment.quote_id)
    requested_comment = edit_comment_by_id(comment_id, new_comment, session)
    return ThemeCommentsResponse(id=requested_comment.id_, theme_id=requested_comment.theme_id,
                                 author_name=requested_comment.author_name, text=requested_comment.text,
                                 quote_id=new_comment.quote_id)


@app.delete("/theme/{theme_id}", response_model=GetThemesResponse)
def delete_theme(theme_id: int):
    requested_theme = delete_theme_by_id(theme_id, session)
    response = GetThemesResponse(id=requested_theme.id_, name=requested_theme.name, description=requested_theme.text)
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8888)
