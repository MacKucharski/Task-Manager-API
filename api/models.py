'''
The data that will be stored in the database will be represented by a collection of classes, 
usually called database models. The ORM layer within SQLAlchemy will do the translations required to 
map objects created from these classes into rows in the proper database tables.

The sqlalchemy module includes general purpose database functions and classes such as types and query building helpers, 
while sqlalchemy.orm provides the support for using models. 
'''

from typing import Optional, Literal
import sqlalchemy as sa
import sqlalchemy.orm as so
from datetime import datetime, timedelta, timezone
import secrets
from api import db

STATUS = Literal['new', 'in_progress', 'on_hold', 'finished', 'canceled']


class PaginatedAPIMixin():

    @staticmethod
    def obj_to_collection_dict(query, page, per_page):
        resources = db.paginate(query, page=page, per_page=per_page, error_out=False)
        
        data = {
            'items': [item.obj_to_dict() for item in resources.items],
            '_meta': {
                'page' : page,
                'per_page' : per_page,
                'total_pages' : resources.pages,
                'total_items' : resources.total
            }
        }

        return data


class User(db.Model, PaginatedAPIMixin):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    role: so.Mapped[Optional[str]] = so.mapped_column(sa.String(32))
    token: so.Mapped[Optional[str]] = so.mapped_column(sa.String(32), index=True, unique=True)
    token_expiration: so.Mapped[Optional[datetime]]

    tasks: so.WriteOnlyMapped['Task'] = so.relationship(back_populates='assignee')

    def __repr__(self):
        return "<User {}, email: {}>".format(self.username, self.email)
    
    def obj_to_dict(self):
        return {
            'username': self.username,
            'email' : self.email
            }
    
    def get_token(self, expires_in=3600):
        now = datetime.now(timezone.utc)
        if self.token and self.token_expiration.replace(
            tzinfo=timezone.utc) > now + timedelta(seconds=60):
            return self.token
        self.token = secrets.token_hex(16)
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.now(timezone.utc) - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = db.session.scalar(sa.select(User).where(User.token == token))
        if not user or user.token_expiration.replace(
            tzinfo=timezone.utc) < datetime.now(timezone.utc):
            return None
        
        return user



class Task(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    project: so.Mapped[str] = so.mapped_column(sa.String(80))
    name: so.Mapped[str] = so.mapped_column(sa.String(80))
    description: so.Mapped[str] = so.mapped_column(sa.String(140))
    status: so.Mapped[STATUS] = so.mapped_column(sa.Enum('new', 'in_progress', 'on_hold', 'finished', 'canceled', name='status_enum'), default='new', server_default='new')
    username: so.Mapped[Optional[str]] = so.mapped_column(sa.ForeignKey(User.username), index=True)

    assignee : so.Mapped[User] = so.relationship(back_populates='tasks')

    def __repr__(self):
        return "<Task object. Project: {}, name: {}, status: {}, username: {}>".format(self.project, self.name, self.status, self.username)
    
    def obj_to_dict(self):
        return {
            'id': self.id, 
            'project': self.project, 
            'description': self.description, 
            'status':self.status,
            'username': self.username
            }