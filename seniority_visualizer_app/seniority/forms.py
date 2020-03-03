from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, BooleanField


class BuildPilotPlotForm(FlaskForm):
    employee_id = IntegerField("employee_id")
    pin_pilot_group = BooleanField(default=True)

