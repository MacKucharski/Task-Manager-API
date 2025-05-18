from api import api
from flask import jsonify
from werkzeug.exceptions import HTTPException
from typing import Tuple, Optional


@api.errorhandler(HTTPException)
def http_error(error):
    payload = {
        'error': error.name, 
        'message': error.description,
        'status': error.code
        }
    return jsonify(payload), error.code