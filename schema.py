from marshmallow import Schema,fields
from werkzeug.datastructures import FileStorage

class FileStorageField(fields.Field):
    default_error_messages={"invalid":"not a valid image"}
    def _deserialize(self, value, attr, data ):
        if value is None:
            return None
        elif not isinstance(value,FileStorage):
            self.fail("invalid")
        return value

class ImageSchema(Schema):
    image=FileStorageField(required=True)
class plainItemschema(Schema):
    id=fields.Int(dump_only=True)
    name=fields.Str(required=True)
    description=fields.Str(required=True)
    price=fields.Float(required=True)
    
class updateitemschema(Schema):
    name=fields.Str()
    price=fields.Float()
    store_id=fields.Int()
class plaintagschema(Schema):
    id=fields.Int(dump_only=True)
    name=fields.Str()
class plainstoresschema(Schema):
    id=fields.Int(dump_only=True)
    name=fields.Str(required=True)

class Itemschema(plainItemschema):
    store_id=fields.Int(required=True,load_only=True)
    store=fields.Nested(plainstoresschema(),dump_only=True)
    tags=fields.List(fields.Nested(plaintagschema()),dump_only= True)

class storeschema(plainstoresschema):
    items=fields.List(fields.Nested(plainItemschema()),dump_only=True)
    tags=fields.List(fields.Nested(plaintagschema()),dump_only=True)
class tagschema(plaintagschema):
    store_id=fields.Int(load_only=True)
    store=fields.Nested(plainstoresschema(),dump_only=True)
    items=fields.List(fields.Nested(plainItemschema()),dump_only=True)

class tag_itemschema(Schema):
    message=fields.Str()
    item=fields.Nested(Itemschema)
    tag=fields.Nested(tagschema)
class userschema(Schema):
    id=fields.Int(dump_only=True)
    username=fields.Str(required=True)
    password=fields.Str(required=True,load_only=True)
    
class userRegisterschema(userschema):
    email=fields.Str(required=True)
