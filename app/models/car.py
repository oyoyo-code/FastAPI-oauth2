from sqlalchemy import Column, Integer, String, Boolean, DateTime ,ForeignKey
from datetime import datetime

from app.db import Base
from app.models.user import User

class Car(Base):
    __tablename__ = "car"

    id = Column(Integer, autoincrement=True ,primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    buy_num = Column(Integer, autoincrement=True)
    car_name = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    sold_at = Column(DateTime, nullable=False)
    comment = Column(String(1024))
