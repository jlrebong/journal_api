import os

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS

from db import db
from blocklist import BLOCKLIST
from dotenv import load_dotenv

from resources.user import blp as UserBlueprint
from resources.profile import profile_blp as ProfileBluePrint
from resources.file_upload import fileupload_blp as FileUploadBluePrint
from resources.portfolio import port_blp as PortfolioBluePrint
from resources.trades import trades_blp as TradesBluePrint
from resources.charts import charts_blp as ChartsBluePrint

def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()
    CORS(app, support_credentials=True)

    UPLOAD_FOLDER = os.path.join('uploads')
    
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"]  = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL","sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate = Migrate(app, db)

    api = Api(app)

    # Create Instance of the JWT manager
    app.config["JWT_SECRET_KEY"] = "329581613914315419317241218896927899901"
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST
    
    @jwt.revoked_token_loader
    def revoked_token_callback(wt_header, jwt_payload):
        return (
            jsonify({"message": "The token has been revoked", "error": "token revoked"})
        )

    # Adds extra information to a jwt token during creation
    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity==1:
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired", "error": "token expired"})
        )
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify({"message": "The token is invalid", "error": "token invalid"})
        )
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify({"message": "Missing access token", "error": "Access token required"})
        )
     
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(ProfileBluePrint)
    api.register_blueprint(FileUploadBluePrint)
    api.register_blueprint(PortfolioBluePrint)
    api.register_blueprint(TradesBluePrint)
    api.register_blueprint(ChartsBluePrint)

    return app
