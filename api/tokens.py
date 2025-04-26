from api import api, db
from api.auth import basic_auth

@api.route("/api/tokens", methods = ["POST"])
@basic_auth.login_required
def get_token():
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return {'token' : token}