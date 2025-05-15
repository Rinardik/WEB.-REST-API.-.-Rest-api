from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String
from .db_session import SqlAlchemyBase
from sqlalchemy.orm import relationship

class User(UserMixin, SqlAlchemyBase):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    surname = Column(String)
    name = Column(String)
    age = Column(Integer)
    position = Column(String)
    speciality = Column(String)
    address = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    city_from = Column(String)
    jobs = relationship("Job", back_populates="user")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        if not self.hashed_password:
            return False
        return check_password_hash(self.hashed_password, password)