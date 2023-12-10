from marshmallow import Schema, fields

class ProfileSchema(Schema):
    id = fields.Int(required=True)
    firstname = fields.Str(required=True)
    lastname = fields.Str(required=True)
    profile_pic = fields.Str(required=False)
    user_id = fields.Int(required=True, load_only=True)

    print(id)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    is_admin = fields.Bool()
    is_verified = fields.Bool()
    verified_date = fields.Str()

    profile = fields.Nested(ProfileSchema(), dump_only=True)



class LoginSchema(UserSchema):
    keep = fields.Int()