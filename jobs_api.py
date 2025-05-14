from flask import Blueprint, jsonify
from data import db_session
from data.jobs import Job

blueprint = Blueprint('jobs_api', __name__, url_prefix='/api')


@blueprint.route('/jobs', methods=['GET'])
def get_jobs():
    db_sess = db_session.create_session()
    jobs_list = db_sess.query(Job).all()

    return jsonify({
        'jobs': [job.to_dict() for job in jobs_list]
    })


