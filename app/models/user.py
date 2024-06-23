from sqlalchemy import Column, Integer, String

from app.db import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, autoincrement=True ,primary_key=True)
    email = Column(String(1024),nullable=False)
    password = Column(String(1024),nullable=False)
    username = Column(String(1024),nullable=False)
