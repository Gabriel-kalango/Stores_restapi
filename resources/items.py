

from flask.views import MethodView
from flask_smorest import Blueprint,abort
from models import ItemModel
from db import db
from sqlalchemy.exc import SQLAlchemyError
from schema import Itemschema,updateitemschema
from flask_jwt_extended import jwt_required,get_jwt
blb=Blueprint("items",__name__,description="operations on the items")
@blb.route("/item/<int:item_id>")
class item(MethodView):
    @blb.response(200,Itemschema)
    def get(self,item_id):
        item=ItemModel.query.get_or_404(item_id)
        return item
    @jwt_required(fresh=True)
    def delete(self,item_id):
        jwt=get_jwt()
        if not jwt.get("is_admin"):
            abort(400,message="unauthorized user")

        item=ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message":"item has been deleted "}
        

        
    @jwt_required()  
    @blb.arguments(updateitemschema)
    @blb.response(200,Itemschema)
    def put(self,itemdata,item_id):
        
        item=ItemModel.query.get(item_id)
        if item:
            item.price=itemdata["price"]
            item.name=itemdata["name"]
        else:
            item=ItemModel(id=item_id,**itemdata)
        db.session.add(item)
        db.session.commit()
        return item
        
@blb.route("/items")
class itemList(MethodView):
    @blb.response(200,Itemschema(many=True))
    def get(self):
        return ItemModel.query.all()
    
    @blb.arguments(Itemschema)
    @blb.response(201,Itemschema)
    def post(self,itemdata):
        item=ItemModel(**itemdata)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="an error occured while creating the item")
        return item


        
