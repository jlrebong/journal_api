from db import db

class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    is_admin = db.Column(db.Boolean(), default=False)

    is_verified = db.Column(db.Boolean(), default=False)
    verified_date = db.Column(db.String(255), nullable=False)

    profile = db.relationship(
        "ProfileModel", back_populates="profile", lazy="dynamic", cascade="all, delete"
    )

    portfolio = db.relationship(
        "PortfolioModel", back_populates="portfolio", lazy="dynamic", cascade="all, delete"
    )
