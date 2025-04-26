from flask import jsonify, request, abort
# import api from __init__.py
from api import api
from api.logic import get_task_list_all, get_task_list, delete_task, create_new_task, edit_task
from api.auth import token_auth

@api.route("/api/tasks", methods = ["GET"])
@token_auth.login_required
def get_tasks_all():
    '''Returns a list of all tasks from DB (admin only)'''

    token_user = token_auth.current_user()

    response, status = get_task_list_all(token_user)

    return jsonify(response), status


@api.route("/api/task", methods = ["GET"])
@token_auth.login_required
def get_tasks():
    '''Returns a list of tasks filtered using defined parameters'''

    request_data = request.args
    token_user = token_auth.current_user()

    response, status = get_task_list(request_data, token_user)

    return jsonify(response), status


@api.route("/api/task", methods = ['POST'])
@token_auth.login_required
def new_task():
    '''Creates new task (admin only)'''
    
    request_data = request.json
    token_user = token_auth.current_user()

    response, status  = create_new_task(request_data, token_user)
    
    return jsonify({"tasks": response}), status


@api.route("/api/task", methods = ["PUT"])
@token_auth.login_required
def edit():
    '''Edits specified task. Regular user can change status only.'''

    request_data = request.json
    token_user = token_auth.current_user()

    response, status = edit_task(request_data, token_user)

    return jsonify(response), status


@api.route("/api/task", methods = ["DELETE"])
@token_auth.login_required
def delete():
    '''Deletes specified task (admin only)'''
    
    request_data = request.json
    token_user = token_auth.current_user()
    
    response, status = delete_task(request_data, token_user)
    
    return jsonify(response), status