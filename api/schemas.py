# from api import ma
# from api.models import User, Task, STATUS
# from marshmallow import validate, validates, validates_schema, ValidationError

# class UserSchema(ma.SQLAlchemySchema):
#     class Meta:
#         model = User
#         ordered = True
    
#     id = ma.auto_field(dump_only = True)
#     username = ma.auto_field(required = True, validate = validate.Length(min=3, max=64))


# class TaskSchema(ma.SQLAlchemySchema):
#     class Meta:
#         model = Task
#         include_fk = True
#         odered = True
    
#     id = ma.auto_field(dump_only = True)
#     project = ma.auto_field(required = True, validate = validate.Length(min=3, max=140))
#     description = ma.auto_field(required = True, validate = validate.Length(min=3, max=140))
#     status = ma.auto_field(validate = validate.OneOf(STATUS.__args__))
#     user_id = ma.auto_field(dump_only = True)