from flask_restx import Resource, reqparse, Namespace
from flask import jsonify, request
from quantutils.api.datasource import MarketDataStore
import pandas
import json

mds = MarketDataStore("./datasources")

api = Namespace('prices', description='Price operations')


@api.route('/aggregate')
class AggregatePrices(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('start', help='Start timestamp (optional)')
    parser.add_argument('end', help='End timestamp (optional)')
    parser.add_argument('unit', required=True, help='Sample unit for requested data, e.g: 1H, 5min')
    parser.add_argument('sources', action='append', required=True, help='Precedence ordered list of datasources to read from')

    @api.expect(parser, validate=True)
    @api.doc(description='Get prices based on an aggregation of datasources')
    def get(self):

        args = self.parser.parse_args()
        start = args["start"] if args["start"] else "1979-01-01"
        end = args["end"] if args["end"] else "2050-01-01"

        try:
            results = mds.aggregate(args["sources"], args["unit"], start, end, True)
            if results is not None:
                results = results.to_json(orient='split', date_format="iso")
            results = {"rc": "success", "body": results}
        except Exception as e:
            results = {"rc": "fail", "msg": str(e)}
        return jsonify(results)


@api.route('/datasource/<source_id>')
class Prices(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('unit', required=True, help='Sample unit for datasource, e.g: 1H, 5min')

    @api.doc(description='Get price data from a datasource')
    def get(self, source_id):

        try:
            results = mds.get(source_id)
            if results is not None:
                results = results.to_json(orient='split', date_format="iso")
            results = {"rc": "success", "body": results}
        except Exception as e:
            results = {"rc": "fail", "msg": str(e)}
        return jsonify(results)

    @api.expect(parser, validate=True)
    @api.doc(description='Add new price data to a datasource')
    def post(self, source_id):

        args = self.parser.parse_args()
        data = pandas.read_json(json.dumps(request.get_json()), orient='split')
        # Uncomment the following on pandas < 1.2.0
        # data.index = data.index.tz_localize('UTC')

        try:
            mds.append(source_id, data, args["unit"])
            results = {"rc": "success"}
        except ValueError as e:
            results = {"rc": "fail", "msg": str(e)}

        return jsonify(results)

    @api.expect(parser, validate=True)
    @api.doc(description='Add or update existing price data for a datasource')
    def put(self, source_id):

        args = self.parser.parse_args()
        data = pandas.read_json(json.dumps(request.get_json()), orient='split')
        # Uncomment the following on pandas < 1.2.0
        # data.index = data.index.tz_localize('UTC')

        try:
            mds.append(source_id, data, args["unit"], update=True)
            results = {"rc": "success"}
        except ValueError as e:
            results = {"rc": "fail", "msg": str(e)}

        return jsonify(results)

    @api.doc(description='Remove a datasource and all its existing price data')
    def delete(self, source_id):

        try:
            mds.delete(source_id)
            results = {"rc": "success"}
        except Exception as e:
            results = {"rc": "fail", "msg": str(e)}
        return jsonify(results)
