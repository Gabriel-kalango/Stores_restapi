from flask.views import MethodView
from flask_smorest import Blueprint,abort
from models import UserModel,BlockliskModel
from db import db
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from schema import userschema,userRegisterschema
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token,get_jwt,jwt_required,create_refresh_token,get_jwt_identity
import requests
import os
from sqlalchemy import or_

blb=Blueprint("user",__name__,description="user blueprint")
def send_simple_message(to,subject,text):

    domain=os.getenv("MAILGUN_DOMAIN")
    return requests.post(
		f"https://api.mailgun.net/v3/{domain}/messages",
		auth=("api", os.getenv("MAILGUN_API_KEY")),
		data={"from": f"kally group of companies <mailgun@{domain}>",
			"to": [to],
			"subject": subject,
			"text": text})

@blb.route("/register")
class UserRegister(MethodView):
    @blb.arguments(userRegisterschema)
    def post(self,userdata):
        if UserModel.query.filter(
            or_(
                UserModel.username == userdata["username"],
                UserModel.email == userdata["email"]
            )
        ).first():
            abort(409, message="A user with that username or email already exists.")

        user=UserModel(username=userdata["username"],password=pbkdf2_sha256.hash(userdata["password"]),email=userdata["email"])
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            abort(400,message="a user with this name already exist ")
        except SQLAlchemyError:
            abort(400,message="an error occured while creating user ")
        send_simple_message(to=user.email,subject="successfully signed up",text=f"hi! {user.username} you have successfully signed up to kally stores rest api ")
        return {"message":" user has been created successfully"},201

@blb.route("/login")
class userLogin(MethodView):
    @blb.arguments(userschema)
    def post(self,userdata):
        user=UserModel.query.filter(UserModel.username==userdata["username"]).first()
        if user and pbkdf2_sha256.verify(userdata["password"],user.password):
            access_token=create_access_token(identity=user.id,fresh=True)
            refresh_token=create_refresh_token(identity=user.id)
            return {"access_token":access_token,"refresh_token":refresh_token}
        abort(400, message="incorrect username and password")
@blb.route("/refresh")
class refresh_token(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user=get_jwt_identity()
        access_token=create_access_token(identity=current_user,fresh=False)
        return {"access_token":access_token}
@blb.route("/logout")
class userlogout(MethodView):
    @jwt_required()
    def post(self):
        jti=get_jwt().get("jti")
        j_ti=BlockliskModel(jwt=jti)
        db.session.add(j_ti)
        db.session.commit()
        return {"message":"user has been logged out "}




@blb.route("/register/<int:user_id>")
class User(MethodView):
    @blb.response(200,userschema)
    def get(self,user_id):
        user=UserModel.query.get_or_404(user_id)
        return user
    def delete(self,user_id):
        user=UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message":"user has been deleted"},200