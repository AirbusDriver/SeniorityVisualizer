from flask import Blueprint

from .models import PilotRecord, SeniorityListRecord

blueprint = Blueprint(
    "seniority", __name__, url_prefix="/seniority", static_folder="../static"
)
