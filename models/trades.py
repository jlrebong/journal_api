from db import db

class TradesModel(db.Model):
    __tablename__ = "trades"

    id = db.Column(db.Integer, primary_key=True)

    symbol = db.Column(db.String(255), unique=False, nullable=False)
    direction = db.Column(db.String(10),nullable=True)
    strategy = db.Column(db.String(10), nullable=True)
    amount = db.Column(db.String(255), nullable=False)
    entry_price = db.Column(db.String(255), nullable=False)
    sell_price = db.Column(db.String(255), nullable=True)
    target_price = db.Column(db.String(255),nullable=True)
    stop_price = db.Column(db.String(255),nullable=True)
    status = db.Column(db.String(5), nullable=False)
    rating = db.Column(db.String(50),nullable=True)

    comments = db.Column(db.String(1000), nullable=True)
    
    created_date = db.Column(db.String(50), nullable=False)

    closed = db.Column(db.Boolean(), nullable=True)
    closed_date = db.Column(db.String(50), nullable=True)

    portfolio_id = db.Column(db.Integer, db.ForeignKey("portfolios.id"), nullable=True)
    portfolio = db.relationship("PortfolioModel", back_populates="trades")

    @property
    def serialized(self):
        """Return object data in serializeable format"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'direction': self.direction,
            'strategy': self.strategy,
            'amount': self.amount,
            'entry_price': self.entry_price,
            'sell_price': self.sell_price,
            'target_price': self.target_price,
            'stop_price': self.stop_price,
            'status': self.status,
            'comments': self.comments,
            'created_date': self.created_date,
            'closed': self.closed,
            'closed_date': self.closed_date,
            'portfolio_id': self.portfolio_id,
        }