from flask_restx import Resource, fields, reqparse, Namespace
from flask import jsonify, request
from quantutils.api.datasource import MarketDataStore
import pandas
import json

mds = MarketDataStore("./datasources")

api = Namespace('prices', description='Price operations')

# model the input data
price_data = api.model('Provide the price data:',
                       {
                           "market": fields.String,
                           "data": fields.List(fields.List(fields.Float)),
                           "tz": fields.String,
                           "index": fields.List(fields.String)
                       })


@api.route('/<market_id>')
@api.response(404, 'Market not found')
class Prices(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('start')
    parser.add_argument('end')

    @api.doc(params={'start': 'Start timestamp', 'end': 'End timestamp'})
    def get_backup(self, market_id):

        args = self.parser.parse_args()

        assets = {
            "markets": [market_id],
            "start": args["start"] if args["start"] else "1979-01-01",
            "end": args["end"] if args["end"] else "2050-01-01",
        }

        data = mds.loadMarketData(assets, "H")
        if market_id in data:
            results = data[market_id].to_json(orient='split', date_format="iso")
        else:
            api.abort(404)
        return jsonify(results)

    def get(self, market_id):

        try:
            results = mds.getHDF("datasources/test.hdf", market_id)
            results = results.to_json(orient='split', date_format="iso")
        except Exception as e:
            results = {"rc": "fail", "msg": str(e)}
        return jsonify(results)

    def post(self, market_id):

        body = request.get_json()
        data = pandas.read_json(json.dumps(body), orient='split')

        try:
            mds.appendHDF("datasources/test.hdf", market_id, data, "H")
            body = {"rc": "success"}
        except ValueError as e:
            body = {"rc": "fail", "msg": str(e)}

        return body

    def put(self, market_id):

        body = request.get_json()
        data = pandas.read_json(json.dumps(body), orient='split')

        try:
            mds.appendHDF("datasources/test.hdf", market_id, data, "H", update=True)
            body = {"rc": "success"}
        except ValueError as e:
            body = {"rc": "fail", "msg": str(e)}

        return body

    def delete(self, market_id):
        mds.deleteHDF("datasources/test.hdf", market_id)
        return {"rc": "success"}
