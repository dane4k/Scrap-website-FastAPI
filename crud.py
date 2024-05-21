from models import *


def add_object(object_, session):
    session.add(object_)
    session.commit()


def get_objects(object_, session):
    objects_data = session.query(object_).all()
    return objects_data


def get_object(object_, id_, session):
    requested_object = session.query(object_).filter(object_.id_ == id_).first()
    return requested_object


def get_comments_by_theme_id(theme_id, session):
    requested_comments = session.query(Comment).filter(Comment.theme_id == theme_id).all()
    return requested_comments


def edit_comment_by_id(comment_id, new_comment, session):
    requested_comment = session.query(Comment).filter(Comment.id_ == comment_id).first()
    requested_comment.author_name = new_comment.author_name
    requested_comment.text = new_comment.text
    requested_comment.quote_id = new_comment.quote_id
    session.commit()
    return requested_comment


def delete_theme_by_id(theme_id, session):
    requested_theme = session.query(Theme).filter(Theme.id_ == theme_id).first()
    session.delete(requested_theme)
    session.commit()
    return requested_theme
