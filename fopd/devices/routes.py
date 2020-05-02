from flask import Blueprint, request, jsonify

from fopd import db
from fopd.models import Teacher, Experiment

import uuid, datetime

devices = Blueprint('devices', __name__)

ERROR_CODE = 400
SUCCESS_CODE = 200