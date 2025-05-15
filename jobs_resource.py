from flask_restful import Resource, reqparse
from data.jobs import Job
from data.db_session import create_session


job_parser = reqparse.RequestParser()
job_parser.add_argument('job_title', type=str, required=True, help="Job title cannot be blank!")
job_parser.add_argument('team_leader_id', type=int, required=True, help="Team leader ID cannot be blank!")
job_parser.add_argument('work_size', type=int, required=True, help="Work size cannot be blank!")
job_parser.add_argument('collaborators', type=str, required=True, help="Collaborators cannot be blank!")
job_parser.add_argument('is_finished', type=bool, required=True, help="Finished status cannot be blank!")
job_parser.add_argument('category_id', type=int, required=True, help="Category ID cannot be blank!")


class JobsResource(Resource):
    def get(self, job_id):
        db_sess = create_session()
        job = db_sess.query(Job).get(job_id)
        if not job:
            return {'message': 'Job not found'}, 404
        return job.to_dict()

    def put(self, job_id):
        db_sess = create_session()
        job = db_sess.query(Job).get(job_id)
        if not job:
            return {'message': 'Job not found'}, 404

        args = job_parser.parse_args()
        job.job_title = args['job_title']
        job.team_leader_id = args['team_leader_id']
        job.work_size = args['work_size']
        job.collaborators = args['collaborators']
        job.is_finished = args['is_finished']
        job.category_id = args['category_id']

        db_sess.commit()
        return job.to_dict()

    def delete(self, job_id):
        db_sess = create_session()
        job = db_sess.query(Job).get(job_id)
        if not job:
            return {'message': 'Job not found'}, 404
        db_sess.delete(job)
        db_sess.commit()
        return {'message': 'Job deleted successfully'}


class JobsListResource(Resource):
    def get(self):
        db_sess = create_session()
        jobs = db_sess.query(Job).all()
        return {'jobs': [job.to_dict() for job in jobs]}

    def post(self):
        args = job_parser.parse_args()
        db_sess = create_session()
        
        job = Job(
            job_title=args['job_title'],
            team_leader_id=args['team_leader_id'],
            work_size=args['work_size'],
            collaborators=args['collaborators'],
            is_finished=args['is_finished'],
            category_id=args['category_id']
        )
        
        db_sess.add(job)
        db_sess.commit()
        return job.to_dict(), 201