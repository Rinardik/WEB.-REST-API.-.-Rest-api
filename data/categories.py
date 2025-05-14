from sqlalchemy import Column, Integer, String
from .db_session import SqlAlchemyBase

class Category(SqlAlchemyBase):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    hazard_level = Column(Integer, nullable=False)