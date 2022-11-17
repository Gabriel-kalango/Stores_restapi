from flask_smorest import Blueprint,abort
from models import storeModel,TagModel,ItemModel
from sqlalchemy.exc import SQLAlchemyError
from schema import tagschema,tag_itemschema
from flask.views import MethodView
from db import db

blb=Blueprint("tags",__name__,description="tags of a items in a store")
@blb.route("/store/<int:store_id>/tag")
class Tagsinstore(MethodView):
    @blb.response(200,tagschema(many=True))
    def get(self,store_id):
        store=storeModel.query.get_or_404(store_id)
        return store.tags.all()
    
    @blb.arguments(tagschema)
    @blb.response(201,tagschema)
    def post(self,tagdata,store_id):
        tags=TagModel(**tagdata,store_id=store_id)
        try:
            db.session.add(tags)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(400,message=str(e))
        return tags
@blb.route("/item/<int:item_id>/tag/<int:tag_id>")
class linktagtoitem(MethodView):
    @blb.response(201,tagschema)
    def post(self,item_id,tag_id): 
        item=ItemModel.query.get_or_404(item_id)
        tag=TagModel.query.get_or_404(tag_id)
        if item.store.id != tag.store.id:
            abort(400, message="Make sure item and tag belong to the same store before linking.")
        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(400,message="an error occured while linking the tag")
        return tag

    def delete(self,item_id,tag_id):
        item=ItemModel.query.get_or_404(item_id)
        tag=TagModel.query.get_or_404(tag_id)
        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(400,message="an error occured while deleting this tag from the list")
        return {"message":"link has been deleted","item":item,"tag":tag}








@blb.route("/tag/<int:tag_id>")
class tag(MethodView):
    @blb.response(200,tagschema)
    def get(self,tag_id):
        tag=TagModel.query.get_or_404(tag_id)
        return tag
    @blb.response(
        202,
        description="Deletes a tag if no item is tagged with it.",
        example={"message": "Tag deleted."},
    )
    @blb.alt_response(404, description="Tag not found.")
    @blb.alt_response(
        400,
        description="Returned if the tag is assigned to one or more items. In this case, the tag is not deleted.",
    )
    def delete(self,tag_id):
        tag=TagModel.query.get_or_404(tag_id)
        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
        abort(
            400,
            message="ensure that tag is not linked to any item "
        )
