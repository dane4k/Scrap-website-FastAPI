from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

engine = create_engine('sqlite:///database.db')
Base = declarative_base()


class Theme(Base):
    __tablename__ = 'Theme'
    id_ = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    text = Column(String, nullable=False)


class Author(Base):
    __tablename__ = 'Author'
    id_ = Column(Integer, primary_key=True)
    nickname = Column(String, nullable=False)


class Comment(Base):
    __tablename__ = 'Comment'
    id_ = Column(Integer, primary_key=True)
    theme_id = Column(Integer, ForeignKey('Theme.id_'), nullable=False)
    author_id = Column(Integer, ForeignKey('Author.id_'), nullable=False)
    author_name = Column(String, nullable=False)
    quote_id = Column(Integer)
    text = Column(String, nullable=False)
    created = Column(DateTime, nullable=True)
    likes = Column(Integer, nullable=True)
    theme = relationship(Theme)
    author = relationship(Author)
