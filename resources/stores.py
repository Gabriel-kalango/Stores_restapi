
from flask.views import MethodView
from flask_smorest import Blueprint,abort
from db import db 
from models import storeModel
from sqlalchemy.exc import SQLAlchemyError,IntegrityError


from schema import storeschema
blb=Blueprint("stores",__name__,description="operations on the stores")
@blb.route("/store/<string:store_id>")
class store(MethodView):
    @blb.response(200,storeschema)
    def get(self,store_id):
        store=storeModel.query.get_or_404(store_id)
        return store
    def delete(self,store_id):
        store=storeModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message":"store has been deleted "}
        
@blb.route("/stores")
class storeList(MethodView):
    @blb.response(200,storeschema(many=True))
    def get(self):
        return storeModel.query.all()
    @blb.arguments(storeschema)
    @blb.response(201,storeschema)
    def post(self,storedata):
        
        store=storeModel(**storedata)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400,message="a store with this name already exist ")
        except SQLAlchemyError:
            abort(500, message="an error occured while creating the store")
        return store
