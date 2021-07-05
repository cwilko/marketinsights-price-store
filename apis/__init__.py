from flask_restx import Api

from .prices import api as ns1

api = Api(
    title='Price Store API',
    version='1.0',
    description='MarketInsights Price Store API',
    # All API metadatas
)

api.add_namespace(ns1)
