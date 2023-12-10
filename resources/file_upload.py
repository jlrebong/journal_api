from flask import jsonify, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint
from flask_cors import cross_origin
from flask import current_app
import csv

from db import db

# for file upload
import os
from werkzeug.utils import secure_filename

from models.stocks import StocksModel

fileupload_blp = Blueprint("Files", "files", description="File Upload Operation")

@cross_origin(supports_credentials=True)
@fileupload_blp.route("/api/file/upload_stock_csv")
class FileUpload(MethodView):
    @fileupload_blp.response(200)
    def post(self):
        # print(request.files)

        if request.files:
            f= request.files.get('file')
            data_filename  = secure_filename(f.filename)
            data_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], data_filename) 
            f.save(data_filepath)

            with open(data_filepath, 'r') as csv_f:          # Read lines separately
                reader = csv.reader(csv_f, delimiter='|')
                for i, line in enumerate(reader):
                    if i == 0:
                        continue

                    if line[1] == '':
                        continue

                    stock = StocksModel(companyname=line[0],
                                       symbol=line[1],
                                       sectorname=line[2],
                                       subsectorname=line[3],
                                       listingdate=line[4])

                    db.session.add(stock)
                
                db.session.commit()


        return "File Data Uploaded"
    
@cross_origin(supports_credentials=True)
@fileupload_blp.route("/api/file/stock_list")
class FileList(MethodView):
    @jwt_required()
    @fileupload_blp.response(200)
    def get(self):
        results = StocksModel.query.all()
        return jsonify({
            'data': [result.serialized for result in results]
        })