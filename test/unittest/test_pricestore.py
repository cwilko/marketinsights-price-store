import unittest
import os
import json
import hashlib
import numpy as np
import pandas as pd
from marketinsights.remote.datastore import MIDataStoreRemote
from marketinsights.api.aggregator import MarketDataAggregator

dir = os.path.dirname(os.path.abspath(__file__))
sharedDigest = "a42b8d7f7feca51b5f86bdbb3c3ba0f6"


class TestPriceStore(unittest.TestCase):

    def setUp(self):
        HOST = os.getenv('HOSTNAME')
        if not HOST:
            HOST = "localhost"

        self.mds = MIDataStoreRemote(location="http://" + HOST + ":8080")

        # start = "2013-01-01"
        # end = "2013-07-10 18:00"
        # marketData = aggregator.getData("DOW", "H", start, end, debug=True)
        # marketData = ppl.removeNaNs(marketData)

        marketData = pd.read_csv(dir + "/data/test.csv", parse_dates=True, index_col='Date_Time')
        marketData["ID"] = "TestSource"
        marketData = marketData.reset_index().set_index(["Date_Time", "ID"])[["Open", "High", "Low", "Close"]]

        # ts.index = ts.index.tz_localize('UTC')
        # ts = ts.tz_convert("US/Eastern", level=0)

        self.marketData = marketData

    def test_store_and_retrieve_data(self):

        self.mds.append("TestMarket", self.marketData)

        start = "2013-01-01"
        end = "2013-07-10"
        resultData = self.mds.aggregate("TestMarket", ["TestSource"], end=end)
        print(resultData)
        assert self.marketData.equals(resultData)

    def test_store_MDS_and_aggregate(self):

        OHLCData = pd.read_pickle(dir + "/data/DOW_pickle")
        #OHLCData = OHLCData.sort_index().loc[pd.IndexSlice[["D&J-IND", "WallSt-hourly"], "2016-04-10":"2016-04-27"], :]
        # OHLCData.to_pickle("DOW_pickle")
        self.mds.append("DOW", OHLCData)
        print(OHLCData)

        with open(dir + "/data/config_mds.json") as json_file:
            data_config = json.load(json_file)

        start = "2016-04-15"
        end = "2016-04-25"

        # Get data from MDS
        MDS_aggregator = MarketDataAggregator(data_config)

        MDSData = MDS_aggregator.getData("DOW", "D", start, end, debug=False)

        dataHash = hashlib.md5(pd.util.hash_pandas_object(MDSData).values.flatten()).hexdigest()
        print(MDSData)
        assert MDSData.shape == (8, 4)
        # Note this must match the OHLC test hexdigest
        assert dataHash == sharedDigest

if __name__ == '__main__':
    unittest.main()
