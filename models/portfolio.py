from db import db

class PortfolioModel(db.Model):
    __tablename__ = "portfolios"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    total_cash = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    portfolio = db.relationship("UserModel", back_populates="portfolio")

    transactions = db.relationship(
        "PortfolioTransactionsModel", back_populates="portfolio", lazy="dynamic", cascade="all, delete"
    )

    trades = db.relationship(
        "TradesModel", back_populates="portfolio", lazy="dynamic", cascade="all, delete"
    )

    @property
    def serialized(self):
        """Return object data in serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'total_cash': self.total_cash,
            'trades': [trade.serialized for trade in self.trades]
        }
    