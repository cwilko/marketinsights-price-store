# import utilities
from quantutils.api.datasource import MarketDataStore
import quantutils.dataset.pipeline as ppl

# Get Market Data

mds = MarketDataStore("../datasources")

assets = {
    "markets": ["DOW"],
    "start": "2013-01-01",
    "end": "2018-07-11"
}

markets = mds.loadMarketData(assets, "H")
ts = ppl.removeNaNs(markets["DOW"])
ts.index = ts.index.tz_convert("US/Eastern")
