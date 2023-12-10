from flask import abort
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_cors import cross_origin
from flask import jsonify

from db import db
from models import TradesModel
from schemas.portfolio import TradesSchema

trades_blp = Blueprint("Trades", "trades", description="Trades")

@cross_origin(supports_credentials=True)
@trades_blp.route("/api/trades/get_current/<int:portfolio_id>")
class Trades(MethodView):
    @trades_blp.response(200, TradesSchema)
    def get(self,portfolio_id):
        trades = TradesModel.query.filter(TradesModel.portfolio_id == portfolio_id) \
                                  .filter(TradesModel.closed != False)
        if trades:
            return jsonify({
                'data':  [trade.serialized for trade in trades] 
            }) 
        
        return jsonify({
                'data': {}
            })

@cross_origin(supports_credentials=True)
@trades_blp.route("/api/trades/get_closed/<int:portfolio_id>")
class Trades(MethodView):
    @trades_blp.response(200, TradesSchema)
    def get(self,portfolio_id):
        trades = TradesModel.query.filter(TradesModel.portfolio_id == portfolio_id) \
                                  .filter(TradesModel.closed == 1)
        if trades:
            return jsonify({
                'data':  [trade.serialized for trade in trades] 
            }) 
        
        return jsonify({
                'data': {}
            })
    
    
@cross_origin(supports_credentials=True)
@trades_blp.route("/api/trades/get/<int:trade_id>")
class TradesDetails(MethodView):
    @trades_blp.response(200, TradesSchema)
    def get(self,trade_id):
        trade = TradesModel.query.filter(TradesModel.id == trade_id).first()
        if trade:
            return jsonify({
                'data': trade.serialized
            })
        
        return jsonify({
                'data': {}
            })
    

@cross_origin(supports_credentials=True)
@trades_blp.route("/api/trades/save/")
class TradeRegister(MethodView):
    @trades_blp.arguments(TradesSchema)
    @trades_blp.response(200)
    def post(self, trades_data):

        if 'id' in trades_data:
            trade = TradesModel.query.get(trades_data['id'])
            
            for p in trades_data:
                setattr(trade, p, trades_data[p])

            print(trade)
                
        else:
            trade = TradesModel(**trades_data)
            db.session.add(trade)

        db.session.commit()

        return jsonify({
                'data': trade.serialized
            })