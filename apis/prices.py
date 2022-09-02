from flask_restx import Resource, reqparse, Namespace
from flask import jsonify, request
from quantutils.api.datasource import MarketDataStore
from quantutils.api.marketinsights import TradeFramework
import pandas
import json
import uuid

mds = MarketDataStore("./datasources")

api = Namespace('prices', description='Price operations')

subscriptions = {}


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
            results = mds.aggregate(start, end, args["sources"], args["unit"])
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
        data.index = data.index.tz_localize('UTC')

        try:
            mds.append(source_id, data, args["unit"])

            # If any subs registered the publish updates
            self.updateSubscriptions(source_id, data.index[0], data.index[-1])

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
        data.index = data.index.tz_localize('UTC')

        try:
            mds.append(source_id, data, args["unit"], update=True)

            # If any subs registered the publish updates
            self.updateSubscriptions(source_id, data.index[0], data.index[-1])

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

    def updateSubscriptions(source_id, start, end):
        try:
            data = mds.aggregate(start, end, args["sources"], args["unit"])
            if data is not None:
                data = data.to_json(orient='split', date_format="iso")
            tf = TradeFramework(subscription["url"])
            tf.appendAsset(env_uuid, market, data)
        except Exception as e:
            results = {"rc": "fail", "msg": str(e)}
        return jsonify(results)


@api.route('/aggregate/subscription/')
class Subscription(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('unit', required=True, help='Sample unit for requested data, e.g: 1H, 5min')
    parser.add_argument('sources', action='append', required=True, help='Precedence ordered list of datasources to read from')
    parser.add_argument('url', required=True, help='URL for webhook registration', location='json')
    # parser.add_argument('history', required=True, help='Boolean value to indicate whether historical prices should be returned on registration')

    @api.expect(parser, validate=True)
    @api.doc(description='Register a webook for notifications on an aggregation of datasources')
    def post(self):
        args = self.parser.parse_args()
        data = request.get_json()
        if data["url"]:

            # Store subscription info
            s_uuid = str(uuid.uuid4())
            subscriptions[s_uuid] = {
                "id": uuid,
                "sources": args["sources"],
                "unit": args["unit"],
                "url": data["url"]
            }
            results = {"rc": "success", "result": subscriptions[s_uuid]}
        else:
            results = {"rc": "fail", "msg": "URL not provided"}

        return jsonify(results)
