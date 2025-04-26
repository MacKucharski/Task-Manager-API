from api import api


@api.route("/api/user", methods = ["GET"])
def get_user():
    '''Available to admin only'''
    pass


@api.route("/api/users", methods = ["GET"])
def get_users():
    '''Available to admin only'''
    pass


@api.route("/api/user", methods = ["POST"])
def create_user():
    '''Available to admin only'''
    pass

@api.route("/api/user", methods = ["PUT"])
def edit_user():
    '''Available to admin only'''
    pass