from db import db 
class BlockliskModel(db.Model):
    __tablename__="blocklist"
    id=db.Column(db.Integer,primary_key=True)
    jwt=db.Column(db.String(1000), nullable=False)