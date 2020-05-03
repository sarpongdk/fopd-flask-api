from flask import Blueprint, request, jsonify

from fopd.services.http_service import HttpService, TIMEOUT, TOOMANYREDIRECTS

import uuid, datetime

externals = Blueprint('externals', __name__)

ERROR_CODE = 400
SUCCESS_CODE = 200

http = HttpService()

@externals.route('/api/external/login', method = ['POST'])
def get_login_credentials():
    """gets login credentials for the fopd api"""
    credentials = request.json
    if not credentials:
        return jsonify({
            'status': 'fail',
            'message': 'No login credentials provided'
        }), ERROR_CODE

    username = credentials.get('username', None)
    password = credentials.get('password', None)

    if not username or not password:
        return jsonify({
            'status': 'success',
            'message': 'No username or password provided'
        }), SUCCESS_CODE

    login_info = {
        'username': username,
        'password': password
    }    

    login_json = http.login(credentials = login_info)

    if login_json == TIMEOUT:
        return jsonify({
            'status': 'fail',
            'message': 'Request timeout'
        }), ERROR_CODE

    if login_json == TOOMANYREDIRECTS:
        return jsonify({
            'status': 'fail',
            'message': 'Too many redirects, bad url'
        }), ERROR_CODE

    return jsonify({
        'status': 'success',
        'session': login_json['session'],
        'logged_in': login_json['logged_in'],
        'organizations': login_json['organizations']
    }), SUCCESS_CODE


@externals.route('/api/external/observations/<device_id>/<start_date>/<end_date>', methods = ['GET'])
def get_observations(device_id, start_date, end_date):
    """get observations from fopd server, dates should be in the format YYYY-MM-DD"""
    observations, status_code, reason = http.getObservations(device_id, start_date, end_date)

    if status_code / 100 != 2:
        return jsonify({
            'status': 'fail',
            'status_code': status_code,
            'message': reason
        }), ERROR_CODE

    return jsonify({
        'status': 'success',
        'num_observations': len(observations),
        'observations': observations
    }), SUCCESS_CODE

