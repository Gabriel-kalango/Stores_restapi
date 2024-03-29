import os
from flask import Flask,jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from resources.items import blb as itemblueprint
from resources.stores import blb as storesblueprint
from resources.tags import blb as tagsblueprint
from resources.user import blb as Userblueprint
from resources.image import blb as imageblueprint
from libs.image_helper import ImageSet
from flask_uploads import configure_uploads
from db import db
from models import BlockliskModel
import models
from flask_migrate import Migrate
from dotenv import load_dotenv


def create_app(db_url=None):
   
    app = Flask(__name__)
    load_dotenv(".env",verbose=True)
    app.config.from_object("default_config")
    app.config.from_envvar("APPLICATION_SETTINGS")
    
    configure_uploads(app,ImageSet)

    # app.config["PROPAGATE_EXCEPTIONS"] = True
    # app.config["API_TITLE"] = "Stores REST API"
    # app.config["API_VERSION"] = "v1"
    # app.config["OPENAPI_VERSION"] = "3.0.3"
    # app.config["OPENAPI_URL_PREFIX"] = "/"
    # app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    # app.config[
    #     "OPENAPI_SWAGGER_UI_URL"
    # ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    # app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///dat.db")
    # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # app.config["JWT_SECRET_KEY"]="442830361741531832645899122519391797179"
    db.init_app(app)
    migrate=Migrate(app,db)
    api = Api(app)
    jwt=JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return  BlockliskModel.query.filter_by(jwt=jwt_payload["jti"] ).first()


    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )

    @jwt.additional_claims_loader
    def add_additional_claims(identity):
        if identity==1:
            return {"is_admin":True}
        {"is_admin":False}
        
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
        jsonify({"message": "The token has expired.", "error": "token_expired"}),
        401,
    )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    # with app.app_context():
    #     db.create_all()
    api.register_blueprint(itemblueprint)
    api.register_blueprint(storesblueprint)
    api.register_blueprint(tagsblueprint)
    api.register_blueprint(Userblueprint)
    api.register_blueprint(imageblueprint)
    
    return app