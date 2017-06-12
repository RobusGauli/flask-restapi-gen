from flask import jsonify

def record_created_envelop(data):
    return jsonify({
        'status' : 'OK',
        'code' : 200,
        'message' : 'Resource Successfully created.',
        'data' : data
    })

def json_records_envelop(data):
    return jsonify({
        'status' : 'OK',
        'code' : 200,
        'data' : data,
        'message' : 'Success'
    })

def fatal_error_envelop():
    return jsonify({
        'status' : 'OK',
        'code' : 404,
        'message' : 'Unknown Error'
    })

def record_updated_envelop(data):
    return jsonify({
        'status': 'OK',
        'code' : 200,
        'message' : 'Resource Successfully updated',
        'data' : data
    })

def record_notfound_envelop():
    return jsonify({
        'status' : 'Fail',
        'code' : 400,
        'message' : 'Resource not found'
    })

def record_exists_envelop(message=None):
    return jsonify({
        'status' : 'Fail',
        'code' : 404, 
        'message' : message or 'Record already exists!!'
    })

def record_deleted_envelop(message=None):
    return jsonify({
        'status' : 'OK',
        'code' : 200,
        'message' : message or 'Resource deleted successfully'
    })

def data_error_envelop(message=None):
    return jsonify({
        'status' : 'Fail',
        'code': 404,
        'message' : message or 'Value too long'
    })

def validation_error_envelop(message=None):
    return jsonify({
        'status' : 'Fail',
        'code' : 500,
        'message' : message or 'Validation Error'
    })