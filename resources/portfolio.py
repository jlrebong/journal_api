from flask import abort
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_cors import cross_origin
from flask import jsonify, request

from flask_jwt_extended import jwt_required

from db import db
from models import PortfolioModel
from models.portfolio_transactions import PortfolioTransactionsModel
from schemas.portfolio import PortAddCashSchema, PortSetCashSchema, PortfolioSchema

port_blp = Blueprint("Portfolio", "portfolio", description="Portfolio Operation")

@cross_origin(supports_credentials=True)
@port_blp.route("/api/portfolio/get_by_userid/<int:user_id>")
class Portfolio(MethodView):
    @port_blp.response(200, PortfolioSchema)
    def get(self,user_id):
        port = PortfolioModel.query.filter(PortfolioModel.user_id == user_id).first()
        if port:
            return jsonify({
                'data': port.serialized
            })
        else:
            if not user_id:
                abort(400)

            # initialize a starter portfolio
            port = PortfolioModel(
                name="User Portfolio",
                total_cash=1000000,
                user_id=user_id
            )
            db.session.add(port)
            db.session.commit()
            return jsonify({
                'data': port.serialized
            })
        
@cross_origin(supports_credentials=True)
@port_blp.route("/api/portfolio/set-cash/")
class PortSetCash(MethodView):
    @jwt_required()
    @port_blp.arguments(PortSetCashSchema)
    @port_blp.response(200)
    def post(self, data):

        print(data)
        port = PortfolioModel.query.filter(PortfolioModel.id == data['portfolio_id']).first()
        
        print(port)

        if port:
            port.total_cash =  data['total_cash']
            db.session.commit()
            return jsonify({
                    'data': port.serialized
                })
        
        abort(400)

    
@cross_origin(supports_credentials=True)
@port_blp.route("/api/portfolio/add-cash/")
class PortAddCash(MethodView):
    @jwt_required()
    @port_blp.arguments(PortAddCashSchema)
    @port_blp.response(200)
    def post(self, data):

        print(data)
        port = PortfolioModel.query.filter(PortfolioModel.id == data['portfolio_id']).first()

        print(port)

        if port:
            if data['type'] == 'A':
                port.total_cash =  port.total_cash + data['add_cash']
            else:
                port.total_cash =  port.total_cash - data['add_cash']

            transaction = PortfolioTransactionsModel(
                type=data['type'],
                amount=data['add_cash'],
                entry_date=data['entry_date'],
                portfolio_id=port.id
            )
            db.session.add(transaction)
            db.session.commit()
            return jsonify({
                    'data': port.serialized
                })
        
        abort(400)