from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from data.db_session import SqlAlchemyBase


class Department(SqlAlchemyBase):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    chief_id = Column(Integer, ForeignKey('users.id'))
    members = Column(String)
    email = Column(String, unique=True)
    chief = relationship("User")