from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase

class Job(SqlAlchemyBase):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_title = Column(String, nullable=False)
    team_leader_id = Column(Integer, ForeignKey('users.id'))
    work_size = Column(Integer)
    collaborators = Column(String)
    is_finished = Column(Boolean, default=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    user = relationship("User", back_populates="jobs")
    category = relationship("Category")

    def to_dict(self):
        return {
            'id': self.id,
            'job_title': self.job_title,
            'team_leader_id': self.team_leader_id,
            'work_size': self.work_size,
            'collaborators': self.collaborators,
            'is_finished': self.is_finished,
            'hazard_category_id': self.hazard_category_id
        }