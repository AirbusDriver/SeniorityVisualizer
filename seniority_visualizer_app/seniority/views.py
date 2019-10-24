

from flask import Blueprint


blueprint = Blueprint("seniority", __name__, url_prefix="/seniority", static_folder="../static")

from .models import SeniorityListRecord, PilotRecord
