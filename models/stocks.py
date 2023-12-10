from db import db

class StocksModel(db.Model):
    __tablename__ = "stocks"

    id = db.Column(db.Integer, primary_key=True)

    companyname = db.Column(db.String(255), unique=False, nullable=False)
    symbol      = db.Column(db.String(20), unique=True, nullable=False)
    sectorname  = db.Column(db.String(100), unique=False, nullable=True)
    subsectorname = db.Column(db.String(100), unique=False, nullable=True)
    listingdate  = db.Column(db.String(100), unique=False, nullable=True)

    @property
    def serialized(self):
        """Return object data in serializeable format"""
        return {
            'companyname': self.companyname,
            'symbol': self.symbol,
            'sectorname': self.sectorname,
            'subsectorname': self.subsectorname,
            'listingdate': self.listingdate
        }
