from flask import Blueprint, request, jsonify

from fopd import db
from fopd.models import Student, Teacher, Experiment

import uuid, datetime

observations = Blueprint('observations', __name__)

ERROR_CODE = 400
SUCCESS_CODE = 200


### Observations