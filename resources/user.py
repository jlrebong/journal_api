import datetime
from flask import abort, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt
from flask_cors import cross_origin

from db import db
from blocklist import BLOCKLIST
from models import UserModel
from schemas.user import UserSchema, LoginSchema

blp = Blueprint("Users", "users", description="User Operation")

@cross_origin(supports_credentials=True)
@blp.route("/api/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(200)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, "User already existing")
        
        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"])
        )

        db.session.add(user)
        db.session.commit()

        return { "message": "User created Successfully.",} 

@cross_origin(supports_credentials=True)
@blp.route("/api/user/<string:username>")
class User(MethodView):
    @blp.response(200,UserSchema)
    def get(self,username):
        user = UserModel.query.filter(UserModel.username == username).first()

        if user:
            return user

        abort(400)
    
    @jwt_required()
    @blp.response(200)
    def delete(self,user_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401)
            
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        return { "message": "User Deleted",}

@cross_origin(supports_credentials=True)
@blp.route("/api/users")
class Users(MethodView):
    @jwt_required()
    @blp.response(200,UserSchema(many=True))
    def get(self):
        return UserModel.query.all()
    
@cross_origin(supports_credentials=True)
@blp.route("/api/login")
class Login(MethodView):
    @blp.arguments(LoginSchema)
    def post(self, user_data):
        if(user_data["username"] == '' or user_data["password"] == ''):
            abort(401, "Invalid credentials")

        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()


        # 5 days 
        expires = datetime.timedelta(days=5)
        if user_data.get("keep") == None or user_data.get("keep") == 0:
            # 1 Hour
            expires = datetime.timedelta(seconds=3600)
            print("No Keep Alive")
        else:
            print("Keep Alive")

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True, expires_delta=expires)
            refresh_token = create_refresh_token(identity=user.id, expires_delta=expires)
            return {
                "access_token": access_token, 
                "refresh_token": refresh_token,
                "userid": user.id,
                "username": user.username
                }
        
        abort(401, "Invalid credentials")


@cross_origin(supports_credentials=True)
@blp.route("/api/changepassword")
class Login(MethodView):
    @blp.arguments(LoginSchema)
    def post(self, user_data):
        if(user_data["username"] == '' or user_data["password"] == ''):
            abort(401, "Invalid credentials")

        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()


        # 5 days 
        # add password logic here
        if user:
            print(user)
            user.password = password=pbkdf2_sha256.hash(user_data["password"])
            db.session.commit()
            return { "message": "Password Updated",}
        
        return abort(401, "Cannot save password")



@cross_origin(supports_credentials=True)
@blp.route("/api/logout")
class Logout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return jsonify({"message": "Logged out."})

@cross_origin(supports_credentials=True)    
@blp.route("/api/refresh")
class Refresh(MethodView):
    @jwt_required(refresh=True)
    def get(self):
        current_user = get_jwt_identity()
        new_token=create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}

@blp.route("/api/tester")
class Refresh(MethodView):
    def get(self):
        return {"is_live": "API is LIVE"}