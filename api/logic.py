from api import db
from api.models import User, Task
from flask import current_app, request, abort
import sqlalchemy as sa
import functools

ATTRIBUTES = ["id", "project", "name", "description", "status", "username"]


def filter_request_parameters(func):
    '''Decorator function to filter out all attributes that do not comply with the schema'''

    @functools.wraps(func)
    def filter_attributes(*args, **kwargs):
        # get data from body
        if data:= request.get_json(force= True, silent= True):
            request_data_unfiltered = data
        # get data from query params
        else:
            request_data_unfiltered = request.args
        
        # !!! schema check to be added
        filtered_data = {key : request_data_unfiltered.get(key, None) for key in ATTRIBUTES}
        return func(*args, filtered_data, **kwargs)
    return filter_attributes


def check_admin(token_user):
    '''Decorator function to check if the token user has admin rights'''

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            user = token_user()
            if user.role != 'admin':
                current_app.logger.error(f"Authorization error. User: {token_user()}")
                description = "You don't have the permission to access the requested resource."
                abort(403, description=description)
            return func(*args, user, **kwargs) 
        return wrapper
    return decorator


def check_username(username: str) -> str:
    '''Helper function to check if username is stored in the DB'''

    if username:
        # check if username in DB
        if not get_user(username):
            message = "Invalid username"
            abort(404, description=message)
        return username


def check_task_id(task_id: str) -> Task:
    '''Helper function to check if task id is provided in request data and if it is stored in the DB'''

    if not task_id:
        message = "Missing task id."
        abort(400, description=message)
    else:
        # check if task in DB 
        task = get_task(task_id)
        if not task:
            message = "Invalid task id."
            abort(404, description=message)
    return task


def get_user(username: str) -> User:
    '''Helper function to get user object from the DB'''

    query = sa.select(User).where(User.username == username)

    return db.session.scalar(query)


def get_task(task_id: int) -> Task:
    '''Helper function to get task object from DB'''

    return db.session.get(Task, task_id)


def get_task_list_all() -> list[dict]:
    '''Gets list of all tasks stored in the DB'''

    query = sa.select(Task)
    task_objects = db.session.scalars(query).all()

    tasks = [task.obj_to_dict() for task in task_objects]

    return tasks, 200


def get_task_list(request_data: dict, token_user: User) -> list[dict]:
    '''Gets a filtered list of tasks based on the parameters provided'''

    # if username in query params, check if user exists in DB
    username = check_username(request_data["username"])

    # check if token_user corresponds to username in query parameters, only admins can check other user's tasks
    if username and username != token_user.username and token_user.role != 'admin':
        current_app.logger.error(f"Authorization error. Function: get_task_list(). User: {token_user}")
        message = "You don't have the permission to access the requested resource."
        abort(403, description=message)

    # if user is not admin and there is no username in query parameters, add token_user.username to request_data dict
    if not username and token_user.role != 'admin':
        request_data = dict(request_data)
        request_data['username'] = token_user.username
    
    condition = [getattr(Task, key, None) == request_data[key] for key in ATTRIBUTES if request_data[key]]
    
    # if no parameters specified - no communication with the DB, return an empty list
    if not condition:
        return [], 200
    
    # construct query based on the condition
    query = sa.select(Task).where(*condition)
    task_objects = db.session.scalars(query).all()
    
    tasks = [task.obj_to_dict() for task in task_objects]
    
    return tasks, 200


def create_new_task(request_data: dict, token_user: User) -> dict:
    '''Creates new task based on provided input'''

    # remove 'id' key from request_data for further processing of the data
    request_data.pop('id')

    for key, value in request_data.items():
        if not value:
            # username is the only parameter that can be empty - task can be unassigned
            if key == 'username':
                check_username(request_data[key])
            
            # all other parameters have to be provided
            else:
                message = "Invalid input. Required fields - project, task name, description, status."
                abort(400, description=message)

    task = Task()
    for key, value in request_data.items():
        if value:
            setattr(task, key, value)

    # save the task in the DB
    try:
        db.session.add(task)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"DB commit failed: {e}. User {token_user}")
        abort(500, description=str(e))

    return task.obj_to_dict(), 201


def edit_task(request_data: dict, token_user: User) -> dict:
    '''Finds task by its id and edits task object based on provided parameters'''

    # check if task id is provided in query parameters and if it is a valid one
    task = check_task_id(request_data["id"])

    # compare username in task with current_user (only admins can change other user's tasks)
    if task.username != token_user.username and token_user.role != 'admin':
        current_app.logger.error(f"Authorization error. User: {token_user}")
        message = "You don't have the permission to access the requested resource."
        abort(403, description=message)
        
    # remove 'id' key from request_data for further processing of the data
    request_data.pop('id')

    if token_user.role == 'admin':
        # verify username when request comes from admin
        check_username(request_data["username"])
        
        if all(value is None for value in request_data.values()) == True:
            # if all values are None - nothing to change
            return {}, 200
        else:    
        # set attributes according to request
            for key, value in request_data.items():
                if value:
                    setattr(task, key, value)
    else:
        if status:= request_data['status']:
            setattr(task, 'status', status)
        else:
            # if status is None - nothing to change
            return {}, 200
    
    # save changes in the DB
    try:
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"DB commit failed: {e}. User {token_user}")
        abort(500, description=str(e))

    return task.obj_to_dict(), 200


def delete_task(request_data: dict, token_user: User) -> dict:
    '''Finds task by its id and deletes it from the DB'''

    # check if task id is provided in query parameters and if it is a valid one
    task = check_task_id(request_data["id"])

    # proceed with deleting the task from DB
    try:
        db.session.delete(task)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"DB commit failed: {e}. User {token_user}")
        abort(500, str(e))

    return {}, 204