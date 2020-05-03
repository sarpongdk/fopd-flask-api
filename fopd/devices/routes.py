from flask import Blueprint, request, jsonify

from fopd import db
from fopd.models import Teacher, Experiment, Device

import uuid, datetime

devices = Blueprint('devices', __name__)

ERROR_CODE = 400
SUCCESS_CODE = 200

# def get_all_devices():
#     """return all devices regardless of teacher"""
#     pass

@devices.route('/api/device/teacher/<teacher_id>', methods = ['GET'])
def get_all_teacher_devices(teacher_id):
    """get a list of teacher's devices"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': f'Account with id {teacher_id} does not exist'
        }), ERROR_CODE

    devices = []
    for device in teacher.devices:
        devices.append({
            'name': device.name,
            'id': device.public_id
        })

    return jsonify({
        'status': 'success',
        'num_devices': len(devices),
        'devices': devices
    }), SUCCESS_CODE

@devices.route('/api/device/<device_id>/teacher/<teacher_id>', methods = ['GET'])
def get_specific_teacher_device(teacher_id, device_id):
    """get a spefic device belonging to a specific teacher"""
    teacher = Teacher.query.filter_by(public_id = teacher_id).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': f'Account with id {teacher_id} does not exist'
        }), ERROR_CODE

    device = Device.query.filter_by(public_id = device_id).first()
    if not device:
        return jsonify({
            'status': 'fail',
            'message': f'Device with id {device_id} does not exist'
        }), ERROR_CODE  

    return jsonify({
        'name': device.name,
        'id': device.public_id,
        'teacher': {
            'fname': teacher.fname,
            'lname': teacher.lname,
            'username': teacher.username,
            'public_id': teacher.public_id
        }
    }), SUCCESS_CODE     

@devices.route('/api/device/<device_id>', methods = ['PUT', 'POST'])
def remove_teacher_ownership(device_id):
    """remove teacher's ownership over device"""
    device = Device.query.filter_by(public_id = device_id).first()
    if not device:
        return jsonify({
            'status': 'fail',
            'message': f'Device with id {device_id} does not exist'
        }), ERROR_CODE  

    device.teacher = None

    try:
        db.session.add(device)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': f'Revoked teacher rights to device id `{device_id}`'
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': f'Unable to create device'
        }), ERROR_CODE


@devices.route('/api/device', methods = ['POST'])
def register_device():
    """register new device"""
    device_info = request.json
    if not device_info:
        return jsonify({
            'status': 'fail',
            'message': 'No information provided'
        }), ERROR_CODE

    #teacher_id = device_info.get('teacher_username', None) # if username is preferred 
    teacher_id = device_info.get('teacher_id', None)
    if not teacher_id:
        return jsonify({
            'status': 'fail',
            'message': 'Cannot register device without teacher'
        }), ERROR_CODE

    teacher = Teacher.query.filter_by(public_id = teacher_id).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': f'Account with id {teacher_id} does not exist'
        }), ERROR_CODE

    device = Device(
        name = device_info.get('name', ''),
        teacher = teacher,
        public_id = str(uuid.uuid4())
    )

    try:
        db.session.add(device)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': f'Successfully created',
            'device': {
                'name': device.name,
                'id': device.public_id,
                'teacher': {
                    'fname': teacher.fname,
                    'lname': teacher.lname,
                    'username': teacher.username,
                    'id': teacher.public_id
                }
            }
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': f'Unable to create device'
        }), ERROR_CODE

@devices.route('/api/device/<device_id>/teacher/<teacher_id>', methods = ['PUT', 'POST'])
def update_device(device_id, teacher_id):
    """update device"""
    device_info = request.json
    if not device_info:
        return jsonify({
            'status': 'fail',
            'message': 'No information provided'
        }), ERROR_CODE

    teacher = Teacher.query.filter_by(public_id = teacher_id).first()
    if not teacher:
        return jsonify({
            'status': 'fail',
            'message': f'Account with id {teacher_id} does not exist'
        }), ERROR_CODE

    device = Device.query.filter_by(public_id = device_id).first()
    if not device:
        return jsonify({
            'status': 'fail',
            'message': f'Device with id {device_id} does not exist'
        }), ERROR_CODE  

    if device.teacher != teacher:
        return jsonify({
            'status': 'fail',
            'message': f'Teacher id `{teacher_id}` does not have permissions to modify device {device_id}'
        }), ERROR_CODE  

    device.name = device_info.get('name', '')

    try:
        db.session.add(device)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': f'Successfully updated',
            'device': {
                'name': device.name,
                'id': device.public_id,
                'teacher': {
                    'fname': teacher.fname,
                    'lname': teacher.lname,
                    'username': teacher.username,
                    'id': teacher.public_id
                }
            }
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': f'Unable to update device `{device_id}`'
        }), ERROR_CODE

        

@devices.route('/api/device/<device_id>', methods = ['DELETE'])
def delete_device(device_id):
    """delete a device"""
    device = Device.query.filter_by(public_id = device_id).first()
    if not device:
        return jsonify({
            'status': 'fail',
            'message': f'Device with id {device_id} does not exist'
        }), ERROR_CODE  

    try:
        db.session.delete(device)
        db.session.commit()
        return jsonify({
            'status': 'fail',
            'message': f'Device id `{device_id}` has been deleted'
        }), SUCCESS_CODE
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'fail',
            'message': f'Unable to delete device id `{device_id}`'
        }), ERROR_CODE