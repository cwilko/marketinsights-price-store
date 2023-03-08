import unittest
import os
import json
import numpy as np
import pandas as pd
from quantutils.api.datasource import MIDataStoreRemote

dir = os.path.dirname(os.path.abspath(__file__))


class PriceStoreTest(unittest.TestCase):

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

        self.mds.append("DOW", self.marketData)

        resultData = self.mds.aggregate("DOW", ["TestSource"])
        print(self.marketData.compare(resultData))
        self.assertTrue(self.marketData.equals(resultData))

if __name__ == '__main__':
    unittest.main()
