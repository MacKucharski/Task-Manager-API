from api import api, db
from api.models import User, Task
import sqlalchemy as sa
import sqlalchemy.orm as so

@api.shell_context_processor
def make_shell_context():
    return {'sa' : sa, 'so' : so, 'db' : db, 'User' : User, 'Task' : Task}