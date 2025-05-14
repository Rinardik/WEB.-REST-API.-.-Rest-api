from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class DepartmentForm(FlaskForm):
    title = StringField('Название департамента', validators=[DataRequired()])
    chief_id = StringField('ID руководителя', validators=[DataRequired()])
    members = TextAreaField('Участники (через запятую)')
    email = StringField('Email департамента')
    submit = SubmitField('Сохранить')