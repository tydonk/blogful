from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from . import app

from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime

class User(Base, UserMixin):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    email = Column(String(128), unique=True)
    password = Column(String(128))
    entries = relationship("Entry", backref="author")
    
class Entry(Base):
    __tablename__ = "entries"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(1024))
    content = Column(Text)
    datetime = Column(DateTime, default=datetime.datetime.now)
    author_id = Column(Integer, ForeignKey('users.id'))
    
Base.metadata.create_all(engine)