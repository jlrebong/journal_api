from db import db

class PortfolioTransactionsModel(db.Model):
    __tablename__ = "portfolio_transactions"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)

    amount = db.Column(db.Integer)

    entry_date = db.Column(db.String(255), nullable=False)

    portfolio_id = db.Column(db.Integer, db.ForeignKey("portfolios.id"), nullable=True)
    portfolio = db.relationship("PortfolioModel", back_populates="transactions")
    
    