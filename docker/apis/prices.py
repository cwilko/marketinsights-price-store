from flask_restx import Resource, reqparse, Namespace
from flask import jsonify, request
from MIPriceStore.api.datasource import MIDataStore
import pandas
import json

# Any change to the following needs a change to the PVC location
mds = MIDataStore("./datasources")

api = Namespace('prices', description='Price operations')


@api.route('/keys')
class Keys(Resource):

    @api.doc(description='Get all datastore tables')
    def get(self):

        try:
            results = mds.getKeys()
            results = {"rc": "success", "body": results}
        except Exception as e:
            results = {"rc": "fail", "msg": str(e)}
        return jsonify(results)


@api.route('/aggregate/<table_id>')
class AggregatePrices(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('start', help='Start timestamp (optional)')
    parser.add_argument('end', help='End timestamp (optional)')
    parser.add_argument('sources', action='append', required=True, help='Precedence ordered list of datasources to read from')

    @api.expect(parser, validate=True)
    @api.doc(description='Get prices based on an aggregation of datasources')
    def get(self, table_id):

        args = self.parser.parse_args()
        start = args["start"] if args["start"] else "1979-01-01"
        end = args["end"] if args["end"] else "2050-01-01"

        try:
            results = mds.aggregate(table_id, args["sources"], start, end, debug=True)
            if results is not None:
                results = results.reset_index().to_json(orient='split', date_format="iso")
            results = {"rc": "success", "body": results}
        except Exception as e:
            results = {"rc": "fail", "msg": str(e)}
        return jsonify(results)


@api.route('/datasource/<table_id>')
class Prices(Resource):

    @api.doc(description='Get price data from a datasource')
    def get(self, table_id):

        try:
            results = mds.get(table_id)
            if results is not None:
                results = results.reset_index().to_json(orient='split', date_format="iso")
            results = {"rc": "success", "body": results}
        except Exception as e:
            results = {"rc": "fail", "msg": str(e)}
        return jsonify(results)

    @api.doc(description='Add new price data to a datasource')
    def post(self, table_id):

        data = pandas.read_json(json.dumps(request.get_json()), orient='split', dtype=False).set_index(["Date_Time", "ID"])
        # Uncomment the following on pandas < 1.2.0
        # data.index = data.index.tz_localize('UTC')

        try:
            mds.append(table_id, data)
            results = {"rc": "success"}
        except ValueError as e:
            results = {"rc": "fail", "msg": str(e)}

        return jsonify(results)

    @api.doc(description='Add or update existing price data for a datasource')
    def put(self, table_id):

        data = pandas.read_json(json.dumps(request.get_json()), orient='split', dtype=False).set_index(["Date_Time", "ID"])
        # Uncomment the following on pandas < 1.2.0
        # data.index = data.index.tz_localize('UTC')

        try:
            mds.append(table_id, data, update=True)
            results = {"rc": "success"}
        except ValueError as e:
            results = {"rc": "fail", "msg": str(e)}

        return jsonify(results)

    @api.doc(description='Remove a datasource and all its existing price data')
    def delete(self, table_id):

        try:
            mds.delete(table_id)
            results = {"rc": "success"}
        except Exception as e:
            results = {"rc": "fail", "msg": str(e)}
        return jsonify(results)
