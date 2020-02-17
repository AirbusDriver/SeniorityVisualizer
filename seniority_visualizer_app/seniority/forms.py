from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField


class BuildPilotPlotForm(FlaskForm):
    employee_id = IntegerField("employee_id")
