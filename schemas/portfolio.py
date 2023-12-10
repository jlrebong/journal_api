from marshmallow import Schema, fields

class TradesSchema(Schema):
    id = fields.Int(required=False)
    symbol = fields.Str(required=True)
    direction = fields.Str(required=False)
    strategy = fields.Str(required=False)
    amount = fields.Str(required=True)
    entry_price = fields.Str(required=True)
    sell_price = fields.Str(required=False)
    target_price = fields.Str(required=False)
    stop_price = fields.Str(required=False)
    status = fields.Str(required=True)
    comments=fields.Str(required=False)
    rating=fields.Str(required=False)
    created_date=fields.Str(required=False)
    closed=fields.Bool()
    closed_date=fields.Str(required=False)
    portfolio_id = fields.Int(required=True)

class PortfolioSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    total_cash = fields.Int(required=True)
    user_id = fields.Int()

    trades = fields.Nested(TradesSchema(), dump_only=True)

class PortSetCashSchema(Schema):
    portfolio_id = fields.Int(required=True)
    total_cash = fields.Int(required=True)

class PortAddCashSchema(Schema):
    add_cash = fields.Int(required=True)
    portfolio_id = fields.Int(required=True)
    type = fields.Str(required=True)
    entry_date = fields.Str(required=True)