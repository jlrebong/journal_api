from db import db

class ProfileModel(db.Model):
    __tablename__ = "profile"

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(255), unique=False, nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    profile_pic = db.Column(db.String(255), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    profile = db.relationship("UserModel", back_populates="profile")