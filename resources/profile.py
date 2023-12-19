from flask import abort, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt
from flask_cors import cross_origin

from db import db
from models import ProfileModel
from schemas.user import ProfileSchema

profile_blp = Blueprint("Profile", "profile", description="User Profile Operation")

@cross_origin(supports_credentials=True)
@profile_blp.route("/api/profile")
class ProfileRegister(MethodView):
    @jwt_required()
    @profile_blp.arguments(ProfileSchema)
    @profile_blp.response(200, ProfileSchema)
    def post(self, profile_data):

        profile = ProfileModel.query.filter(ProfileModel.user_id == profile_data['user_id']).first()

        print (profile)
        if profile:
            profile.firstname = profile_data['firstname']
            profile.lastname = profile_data['lastname']
        else:
            profile = ProfileModel(**profile_data)
            db.session.add(profile)

        db.session.commit()
        return profile
            

@cross_origin(supports_credentials=True)
@profile_blp.route("/api/profile/<int:user_id>")
class Profile(MethodView):
    @profile_blp.response(200,ProfileSchema)
    def get(self,user_id):
        profile = ProfileModel.query.filter(ProfileModel.user_id == user_id).first()
        if profile:
            return profile

        abort(401, "Profile not found")
    
    
@cross_origin(supports_credentials=True)
@profile_blp.route("/api/profiles")
class Profiles(MethodView):
    @jwt_required()
    @profile_blp.response(200,ProfileSchema(many=True))
    def get(self):
        return ProfileModel.query.all()
    