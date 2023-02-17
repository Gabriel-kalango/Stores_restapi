from flask.views import MethodView
from flask_jwt_extended import jwt_required,get_jwt_identity
from flask_uploads import UploadNotAllowed
from schema import ImageSchema
from flask_smorest import Blueprint
from libs import image_helper
from flask import request
blb=Blueprint("image",__name__,description="operations on image")


image_schema=ImageSchema()
@blb.route("/image")
class Uploadimage(MethodView):
    @jwt_required()
    def post(self):
        data=image_schema.load(request.files)
        user_id=get_jwt_identity()
        folder=f"user_{user_id}"
        try:
            image_path=image_helper.save_image(data['image'],folder=folder)
            basename=image_helper.get_basename(image_path)
            return {'message':f'image with the name {basename} has been uploaded'},201
        except UploadNotAllowed:
            extension=image_helper.get_extension(data['image'])
            return {'message':f'the exension {extension} doesnt apply for images'},400
