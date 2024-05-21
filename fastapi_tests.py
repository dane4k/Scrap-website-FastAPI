from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
import pytest

from route import app
from crud import *
from models import *

client = TestClient(app)

session = sessionmaker(bind=engine)()

themes_lst = [dict(list(theme.__dict__.items())[1:]) for theme in get_objects(Theme, session)]
themes_lst = [{'id_': d['id_'], 'name': d['name'], 'description': d['text']} for d in themes_lst]
themes_lst = [{'id': int(theme['id_']), 'name': theme['name'], 'description': theme['description']} for theme in
              themes_lst]

data_create_theme = {
    "name": "Hi everyone",
    "description": "My name is Boba"
}


@pytest.mark.order1
def test_create_theme():
    response = client.post("/theme/", json=data_create_theme)
    assert response is not None
    assert response.status_code == 200
    response = response.json()
    assert response["id"] > 0
    assert response["name"] == data_create_theme["name"]
    assert response["description"] == data_create_theme["description"]


data_create_comment = {
    "author_name": "Bobik",
    "text": "This topic makes me cry",
    "quote_id": -1
}


@pytest.mark.order2
def test_create_comment():
    response = client.post(f'/comment/{447}', json=data_create_comment)
    assert response is not None
    assert response.status_code == 200
    response = response.json()
    assert response[0]["author_name"] == data_create_comment["author_name"]
    assert response[0]["text"] == data_create_comment["text"]
    assert response[0]["quote_id"] == data_create_comment["quote_id"]


@pytest.mark.order3
def test_get_themes():
    response = client.get("/themes/")
    assert response is not None
    assert response.status_code == 200
    response = response.json()
    assert response == themes_lst


data_get_theme = [dict(list(get_object(Theme, 447, session).__dict__.items())[1:])]
data_get_theme = [{'id_': d['id_'], 'name': d['name'], 'description': d['text']} for d in data_get_theme]
data_get_theme = [{'id': int(theme['id_']), 'name': theme['name'], 'description': theme['description']} for theme in
                  data_get_theme]


@pytest.mark.order4
def test_get_theme():
    response = client.get(f'/theme/{447}')
    assert response is not None
    assert response.status_code == 200
    response = response.json()
    assert response == data_get_theme


data_get_comment_by_theme_id = [{"id": d.id_,
                                 "theme_id": d.theme_id,
                                 "author_name": d.author_name,
                                 "text": d.text,
                                 "quote_id": d.quote_id
                                 } for d in get_comments_by_theme_id(6, session)]


@pytest.mark.order5
def test_get_comments_by_theme_id():
    response = client.get(f'/comment/{6}/comments')
    assert response is not None
    assert response.status_code == 200
    response = response.json()
    assert response == data_get_comment_by_theme_id


data_get_comment_by_id = dict(list(get_object(Comment, 95681, session).__dict__.items())[1:])
expected_keys = {'author_name', 'id_', 'quote_id', 'text', 'theme_id'}
data_get_comment_by_id = dict(item for item in list(data_get_comment_by_id.items()) if item[0] in expected_keys)
data_get_comment_by_id["id"] = data_get_comment_by_id.pop("id_")


@pytest.mark.order6
def test_get_comment_by_id():
    response = client.get(f"/comment/{95681}/details")
    assert response is not None
    assert response.status_code == 200
    response = response.json()
    assert response == data_get_comment_by_id


new_comment = Comment(author_name="Lolik", text="hello im a new member of this forum", quote_id=-1)
data_test_edit_comment_by_id = edit_comment_by_id(78956, new_comment, session)

new_comment = {
    "author_name": new_comment.author_name,
    "text": new_comment.text,
    "quote_id": new_comment.quote_id
}

data_test_edit_comment_by_id = {
    "id": data_test_edit_comment_by_id.id_,
    "theme_id": data_test_edit_comment_by_id.theme_id,
    "author_name": data_test_edit_comment_by_id.author_name,
    "text": data_test_edit_comment_by_id.text,
    "quote_id": data_test_edit_comment_by_id.quote_id
}


@pytest.mark.order7
def test_edit_comment_by_id():
    response = client.put(f"/comment/{78956}/edit", json=new_comment)
    assert response is not None
    assert response.status_code == 200
    response = response.json()
    assert response == data_test_edit_comment_by_id


@pytest.mark.order8
def test_delete_theme_by_id():
    response = client.delete(f"/theme/{830}")
    assert response is not None
    assert response.status_code == 200
    response = response.json()
    assert response['id'] == 830
