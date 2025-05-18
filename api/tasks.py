from api import api
from api.logic import get_task_list_all, get_task_list, delete_task, create_new_task, edit_task, filter_request_parameters, check_admin
from api.auth import token_auth

@api.route("/api/tasks", methods = ["GET"])
@token_auth.login_required
@check_admin(lambda: token_auth.current_user())
def get_tasks_all(token_user):
    '''Returns a list of all tasks from DB (admin only)'''

    response, status = get_task_list_all()

    return response, status


@api.route("/api/task", methods = ["GET"])
@token_auth.login_required
@filter_request_parameters
def get_tasks(filtered_data):
    '''Returns a list of tasks filtered using defined parameters'''

    request_data = filtered_data
    token_user = token_auth.current_user()

    response, status = get_task_list(request_data, token_user)

    return response, status


@api.route("/api/task", methods = ['POST'])
@token_auth.login_required
@check_admin(lambda: token_auth.current_user())
@filter_request_parameters
def new_task(token_user, filtered_data):
    '''Creates new task (admin only)'''
    
    request_data = filtered_data
    
    response, status  = create_new_task(request_data, token_user)

    return {"task": response}, status


@api.route("/api/task", methods = ["PUT"])
@token_auth.login_required
@filter_request_parameters
def edit(filtered_data):
    '''Edits specified task. Regular user can change status only.'''

    request_data = filtered_data
    token_user = token_auth.current_user()

    response, status = edit_task(request_data, token_user)

    return response, status


@api.route("/api/task", methods = ["DELETE"])
@token_auth.login_required
@check_admin(lambda: token_auth.current_user())
@filter_request_parameters
def delete(token_user, filtered_data):
    '''Deletes specified task (admin only)'''
    
    request_data = filtered_data
    
    response, status = delete_task(request_data, token_user)
    
    return response, status