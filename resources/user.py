from flask.views import MethodView
from flask_smorest import Blueprint,abort
from models import UserModel,BlockliskModel
from db import db
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from schema import userschema
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token,get_jwt,jwt_required

blb=Blueprint("user",__name__,description="user blueprint")
@blb.route("/register")
class UserRegister(MethodView):
    @blb.arguments(userschema)
    def post(self,userdata):
        user=UserModel(username=userdata["username"],password=pbkdf2_sha256.hash(userdata["password"]),)
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            abort(400,message="a user with this name already exist ")
        except SQLAlchemyError:
            abort(400,message="an error occured while creating user ")
        return {"message":" user has been created successfully"},201

@blb.route("/login")
class userLogin(MethodView):
    @blb.arguments(userschema)
    def post(self,userdata):
        user=UserModel.query.filter(UserModel.username==userdata["username"]).first()
        if user and pbkdf2_sha256.verify(userdata["password"],user.password):
            access_token=create_access_token(identity=user.id)
            return {"access_token":access_token}
        abort(400, message="incorrect username and password")
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