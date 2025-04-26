from api import db
from api.models import User, Task, STATUS
from flask import current_app
import sqlalchemy as sa


def get_user(username: str) -> User:

    query = sa.select(User).where(User.username == username)

    return db.session.scalar(query)


def get_task(task_id: int) -> Task:

    return db.session.get(Task, task_id)


def get_task_list_all(token_user: User) -> list[dict]:
    
    # only admin can request full list
    if token_user.role != 'admin':
        return {
                "error": "Authorization error",
                "message": "You don't have the permission to access the requested resource."
                }, 403
    
    query = sa.select(Task)
    task_objects = db.session.scalars(query).all()

    tasks = [task.obj_to_dict() for task in task_objects]

    return tasks, 200 


def get_task_list(params: dict, token_user: User) -> list[dict]:

    # if username in query params, check if user exists in DB
    if username:= params.get('username', None):
        user = get_user(username)
        
        if not user:
            return {
                "error": "Validation error",
                "message": "Invalid username"
                }, 404

    # check if token_user corresponds to username in query params, only admins/leaders can check other user's tasks
    if username and username != token_user.username and token_user.role != 'admin':
        return {
                "error": "Authorization error",
                "message": "You don't have the permission to access the requested resource."
                }, 403

    # if user is not admin/leader and there is no username in query params, add token_user.username to params dict
    if not username and token_user.role != 'admin':
        params = dict(params)
        params['username'] = token_user.username

    valid_params = ['project', 'name', 'status', 'username']
    
    condition = [getattr(Task, key, None) == value for key, value in params.items() if value and key in valid_params]
    
    # if no params specified - validation error
    if not condition:
        return {
                "error": "Validation error",
                "message": "Missing or invalid query parameters"
                }, 404
    
    # construct query based on the condition
    query = sa.select(Task).where(*condition)
    task_objects = db.session.scalars(query).all()
    
    tasks = [task.obj_to_dict() for task in task_objects]
    
    return tasks, 200


def create_new_task(request_data: dict, token_user: User) -> dict:
    
    # only admin can create new tasks
    if token_user.role != 'admin':
        return {
                "error": "Authorization error",
                "message": "You don't have the permission to create new tasks."
                }, 403

    # sanitizing input data
    data = {}
    required_attributes = ["project", "name", "description", "status"]

    for attribute in required_attributes:
        if value:= request_data.get(attribute, None):
            # add schema check for value!
            data[attribute] = value
        else:
            return {
                "error": "Validation error",
                "message": "Invalid input. Required fields - project, task name, description, status."
            }, 400
    
    if username:= request_data.get("username", None):
        # add schema check for username
        # check if user in DB
        user = get_user(username)
        if not user:
                return {
                "error": "Validation error",
                "message": "Invalid user id."
                }, 404

    task = Task()

    for key, value in data.items():
        setattr(task, key, value)
    
    try:
        db.session.add(task)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return {"error": "Database error", "message": str(e)}, 500

    return {"message" : "Task {} has been created: {}".format(task.id, data)}, 201


def edit_task(request_data: dict, token_user: User) -> dict:

    # check if task_id in request
    task_id = request_data.get("task_id", None)
    if not task_id:
        return {
            "error": "Validation error",
            "message": "Missing task id."
            }, 400
    
    # check if task in DB 
    task = get_task(int(request_data["task_id"]))
    if not task:
        return {
            "error": "Validation error",
            "message": "Invalid task id."
            }, 404
        
    # compare username in task with current_user (only admins can change other user's tasks)
    if task.username != token_user.username and token_user.role != 'admin':
        return {
                "error": "Authorization error",
                "message": "You don't have the permission to modify the requested resource."
                }, 403
    
    # if username provided, check if user in DB
    if username:= request_data.get("username", None):
        if not get_user(username):
            return {
                "error": "Validation error",
                "message": "Invalid username."
                }, 404

    # sanitizing input data
    data = {}
    valid_params = ["project", "name", "description", "status", "username"]

    # admins can change all parameters
    if token_user.role == 'admin':
        for key in valid_params:
            if request_data.get(key, None):
                # add schema validation
                data[key] = request_data[key]

    # regular users can only change the status
    else:
        if status := request_data.get("status", None):
            # add schema validation
            data["status"] = status

    # if data is empty -> no valid params specified, there is nothing to change
    if not data:
        return {
            "error": "Validation error",
            "message": "Missing input."
            }, 400
    
    # set attributes according to valid attributes from request
    for key, value in data.items():
        setattr(task, key, value)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {"error": "Database error", "message": str(e)}, 500
    
    message = "Task {} has been changed: {}".format(task_id, data)

    return {"message" : message}, 200


def delete_task(request_data: dict, token_user: User) -> dict:
    
    # only admin can delete tasks
    if token_user.role != 'admin':
        return {
                "error": "Authorization error",
                "message": "You don't have the permission to modify the requested resource."
                }, 403

    # check if task_id in request
    task_id = request_data.get("task_id", None)
    if not task_id:
        return {
            "error": "Validation error",
            "message": "Missing task id."
            }, 400

    # check if task_id is valid
    task = get_task(task_id)
    if not task:
        return {
            "error": "Validation error",
            "message": "Invalid task id."
            }, 404

    # proceed with deleting the task
    try:
        db.session.delete(task)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return {"error": "Database error", "message": str(e)}, 500

    return {"message" : "Task {} deleted from task list.".format(task_id)}, 200