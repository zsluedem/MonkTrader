#
# MIT License
#
# Copyright (c) 2018 WillQ
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import datetime
import gzip
import io
import os
import random
import tempfile
import zlib
from unittest.mock import MagicMock, patch

import pandas
import pytest
from dateutil.relativedelta import relativedelta
from MonkTrader.assets.const import SIDE
from MonkTrader.const import TICK_DIRECTION
from MonkTrader.exception import DataDownloadError
from MonkTrader.exchange.bitmex.const import INSTRUMENT_FILENAME
from MonkTrader.exchange.bitmex.data import (
    BitMexDownloader, BitMexProcessPoints, DatePoint,
)
from MonkTrader.exchange.bitmex.data.download import (
    START_DATE, HDFQuoteStream, HDFTradeStream, QuoteZipFileStream,
    SymbolsStreamRequest, TarStreamRequest, TradeZipFileStream,
)

stream_b = b"""c1,c2,c3,c4
1,2,3,4
5,6,7,8"""

mock_url = 'http://mock.com'

stream_quote = b"""timestamp,symbol,bidSize,bidPrice,askPrice,askSize
2018-12-05D00:00:04.778522000,ADAZ18,256089,9.54e-06,9.55e-06,524060
2018-12-05D00:00:05.045590000,XBTUSD,256081,9.54e-06,9.55e-06,544060
2018-12-05D00:00:07.302458000,XBTZ18,256083,9.54e-06,9.55e-06,574060
"""
stream_quote_gzip = gzip.compress(stream_quote)
stream_quote = zlib.compress(stream_quote)

stream_trade = b"""timestamp,symbol,side,size,price,tickDirection,trdMatchID,grossValue,homeNotional,foreignNotional
2018-12-05D00:00:25.948313000,ADAZ18,Sell,166774,9.54e-06,MinusTick,498350a3-8c03-affd-cf87-e6d8a90b70e5,159102396,166774,1.591024
2018-12-05D00:00:25.948313000,XBTUSD,Sell,11,9.54e-06,ZeroMinusTick,1d004a95-44fa-c75c-47cd-d651ecd41c25,10494,11,0.00010494
2018-12-05D00:00:25.948313000,XBTZ18,Sell,10000,9.54e-06,ZeroMinusTick,214aa626-cb6a-054f-ccf5-da4e14b5fd23,9540000,10000,0.0954
"""
stream_trade_gzip = gzip.compress(stream_trade)
stream_trade = zlib.compress(stream_trade)

stream_symbols = b"""[{"symbol": "XRPH19", "rootSymbol": "XRP", "state": "Open", "typ": "FFCCSX", "listing": "2018-12-17T04:00:00.000Z", "front": "2019-02-22T12:00:00.000Z", "expiry": "2019-03-29T12:00:00.000Z", "settle": "2019-03-29T12:00:00.000Z", "relistInterval": null, "inverseLeg": "", "sellLeg": "", "buyLeg": "", "optionStrikePcnt": null, "optionStrikeRound": null, "optionStrikePrice": null, "optionMultiplier": null, "positionCurrency": "XRP", "underlying": "XRP", "quoteCurrency": "XBT", "underlyingSymbol": "XRPXBT=", "reference": "BMEX", "referenceSymbol": ".BXRPXBT30M", "calcInterval": null, "publishInterval": null, "publishTime": null, "maxOrderQty": 100000000, "maxPrice": 10, "lotSize": 1, "tickSize": 1e-08, "multiplier": 100000000, "settlCurrency": "XBt", "underlyingToPositionMultiplier": 1, "underlyingToSettleMultiplier": null, "quoteToSettleMultiplier": 100000000, "isQuanto": false, "isInverse": false, "initMargin": 0.05, "maintMargin": 0.025, "riskLimit": 5000000000, "riskStep": 5000000000, "limit": null, "capped": false, "taxed": true, "deleverage": true, "makerFee": -0.0005, "takerFee": 0.0025, "settlementFee": 0, "insuranceFee": 0, "fundingBaseSymbol": "", "fundingQuoteSymbol": "", "fundingPremiumSymbol": "", "fundingTimestamp": null, "fundingInterval": null, "fundingRate": null, "indicativeFundingRate": null, "rebalanceTimestamp": null, "rebalanceInterval": null, "openingTimestamp": "2019-01-01T03:00:00.000Z", "closingTimestamp": "2019-01-01T04:00:00.000Z", "sessionInterval": "2000-01-01T01:00:00.000Z", "prevClosePrice": 9.42e-05, "limitDownPrice": null, "limitUpPrice": null, "bankruptLimitDownPrice": null, "bankruptLimitUpPrice": null, "prevTotalVolume": 238952605, "totalVolume": 239002688, "volume": 50083, "volume24h": 15443438, "prevTotalTurnover": 2319660919392, "totalTurnover": 2320132688566, "turnover": 471769174, "turnover24h": 146188755488, "homeNotional24h": 15443438, "foreignNotional24h": 1461.887554879999, "prevPrice24h": 9.505e-05, "vwap": 9.467e-05, "highPrice": 9.54e-05, "lowPrice": 9.401e-05, "lastPrice": 9.428e-05, "lastPriceProtected": 9.428e-05, "lastTickDirection": "ZeroPlusTick", "lastChangePcnt": -0.0081, "bidPrice": 9.434e-05, "midPrice": 9.435e-05, "askPrice": 9.436e-05, "impactBidPrice": 9.434e-05, "impactMidPrice": 9.437e-05, "impactAskPrice": 9.44e-05, "hasLiquidity": true, "openInterest": 32517836, "openValue": 306675711316, "fairMethod": "ImpactMidPrice", "fairBasisRate": 0.01, "fairBasis": 2.3e-07, "fairPrice": 9.431e-05, "markMethod": "FairPrice", "markPrice": 9.431e-05, "indicativeTaxRate": 0, "indicativeSettlePrice": 9.408e-05, "optionUnderlyingPrice": null, "settledPrice": null, "timestamp": "2019-01-01T03:22:50.000Z"}, {"symbol": "BCHH19", "rootSymbol": "BCH", "state": "Open", "typ": "FFCCSX", "listing": "2018-12-17T04:00:00.000Z", "front": "2019-02-22T12:00:00.000Z", "expiry": "2019-03-29T12:00:00.000Z", "settle": "2019-03-29T12:00:00.000Z", "relistInterval": null, "inverseLeg": "", "sellLeg": "", "buyLeg": "", "optionStrikePcnt": null, "optionStrikeRound": null, "optionStrikePrice": null, "optionMultiplier": null, "positionCurrency": "BCH", "underlying": "BCH", "quoteCurrency": "XBT", "underlyingSymbol": "BCHXBT=", "reference": "BMEX", "referenceSymbol": ".BBCHXBT30M", "calcInterval": null, "publishInterval": null, "publishTime": null, "maxOrderQty": 100000000, "maxPrice": 10, "lotSize": 1, "tickSize": 0.0001, "multiplier": 100000000, "settlCurrency": "XBt", "underlyingToPositionMultiplier": 1, "underlyingToSettleMultiplier": null, "quoteToSettleMultiplier": 100000000, "isQuanto": false, "isInverse": false, "initMargin": 0.05, "maintMargin": 0.025, "riskLimit": 5000000000, "riskStep": 5000000000, "limit": null, "capped": false, "taxed": true, "deleverage": true, "makerFee": -0.0005, "takerFee": 0.0025, "settlementFee": 0, "insuranceFee": 0, "fundingBaseSymbol": "", "fundingQuoteSymbol": "", "fundingPremiumSymbol": "", "fundingTimestamp": null, "fundingInterval": null, "fundingRate": null, "indicativeFundingRate": null, "rebalanceTimestamp": null, "rebalanceInterval": null, "openingTimestamp": "2019-01-01T03:00:00.000Z", "closingTimestamp": "2019-01-01T04:00:00.000Z", "sessionInterval": "2000-01-01T01:00:00.000Z", "prevClosePrice": 0.04083, "limitDownPrice": null, "limitUpPrice": null, "bankruptLimitDownPrice": null, "bankruptLimitUpPrice": null, "prevTotalVolume": 352014, "totalVolume": 353539, "volume": 1525, "volume24h": 27515, "prevTotalTurnover": 1477398180000, "totalTurnover": 1483686250000, "turnover": 6288070000, "turnover24h": 111226820000, "homeNotional24h": 27515, "foreignNotional24h": 1112.268200000001, "prevPrice24h": 0.0412, "vwap": 0.04042407, "highPrice": 0.0416, "lowPrice": 0.0388, "lastPrice": 0.0413, "lastPriceProtected": 0.0413, "lastTickDirection": "ZeroMinusTick", "lastChangePcnt": 0.0024, "bidPrice": 0.0413, "midPrice": 0.04135, "askPrice": 0.0414, "impactBidPrice": 0.0413, "impactMidPrice": 0.0414, "impactAskPrice": 0.04145715, "hasLiquidity": true, "openInterest": 24069, "openValue": 99645660000, "fairMethod": "ImpactMidPrice", "fairBasisRate": -0.06, "fairBasis": -0.0006, "fairPrice": 0.0414, "markMethod": "FairPrice", "markPrice": 0.0414, "indicativeTaxRate": 0, "indicativeSettlePrice": 0.042, "optionUnderlyingPrice": null, "settledPrice": null, "timestamp": "2019-01-01T03:22:50.000Z"}, {"symbol": "ADAH19", "rootSymbol": "ADA", "state": "Open", "typ": "FFCCSX", "listing": "2018-12-17T04:00:00.000Z", "front": "2019-02-22T12:00:00.000Z", "expiry": "2019-03-29T12:00:00.000Z", "settle": "2019-03-29T12:00:00.000Z", "relistInterval": null, "inverseLeg": "", "sellLeg": "", "buyLeg": "", "optionStrikePcnt": null, "optionStrikeRound": null, "optionStrikePrice": null, "optionMultiplier": null, "positionCurrency": "ADA", "underlying": "ADA", "quoteCurrency": "XBT", "underlyingSymbol": "ADAXBT=", "reference": "BMEX", "referenceSymbol": ".BADAXBT30M", "calcInterval": null, "publishInterval": null, "publishTime": null, "maxOrderQty": 100000000, "maxPrice": 10, "lotSize": 1, "tickSize": 1e-08, "multiplier": 100000000, "settlCurrency": "XBt", "underlyingToPositionMultiplier": 1, "underlyingToSettleMultiplier": null, "quoteToSettleMultiplier": 100000000, "isQuanto": false, "isInverse": false, "initMargin": 0.05, "maintMargin": 0.025, "riskLimit": 5000000000, "riskStep": 5000000000, "limit": null, "capped": false, "taxed": true, "deleverage": true, "makerFee": -0.0005, "takerFee": 0.0025, "settlementFee": 0, "insuranceFee": 0, "fundingBaseSymbol": "", "fundingQuoteSymbol": "", "fundingPremiumSymbol": "", "fundingTimestamp": null, "fundingInterval": null, "fundingRate": null, "indicativeFundingRate": null, "rebalanceTimestamp": null, "rebalanceInterval": null, "openingTimestamp": "2019-01-01T03:00:00.000Z", "closingTimestamp": "2019-01-01T04:00:00.000Z", "sessionInterval": "2000-01-01T01:00:00.000Z", "prevClosePrice": 1.1e-05, "limitDownPrice": null, "limitUpPrice": null, "bankruptLimitDownPrice": null, "bankruptLimitUpPrice": null, "prevTotalVolume": 416223681, "totalVolume": 416724252, "volume": 500571, "volume24h": 46652383, "prevTotalTurnover": 450215240966, "totalTurnover": 450761475947, "turnover": 546234981, "turnover24h": 51582221579, "homeNotional24h": 46652383, "foreignNotional24h": 515.82221579, "prevPrice24h": 1.124e-05, "vwap": 1.106e-05, "highPrice": 1.13e-05, "lowPrice": 1.088e-05, "lastPrice": 1.094e-05, "lastPriceProtected": 1.094e-05, "lastTickDirection": "ZeroPlusTick", "lastChangePcnt": -0.0267, "bidPrice": 1.093e-05, "midPrice": 1.0935e-05, "askPrice": 1.094e-05, "impactBidPrice": 1.093e-05, "impactMidPrice": 1.0945e-05, "impactAskPrice": 1.096e-05, "hasLiquidity": true, "openInterest": 44278456, "openValue": 48440630864, "fairMethod": "ImpactMidPrice", "fairBasisRate": 0.04, "fairBasis": 1e-07, "fairPrice": 1.094e-05, "markMethod": "FairPrice", "markPrice": 1.094e-05, "indicativeTaxRate": 0, "indicativeSettlePrice": 1.084e-05, "optionUnderlyingPrice": null, "settledPrice": null, "timestamp": "2019-01-01T03:22:25.000Z"}]"""  # noqa: E501


def _mock_stream(self, url: str):
    s = 0
    while 1:
        ori = s
        s += random.randint(0, 10)

        yield self._stream[ori:s]

        if s > len(self._stream):
            break


def _mock_exception_stream(self, url: str):
    s = 0
    while 1:
        ori = s
        s += random.randint(0, 10)

        yield self._stream[ori:s]

        if s > len(self._stream):
            raise Exception()


def test_datepoint():
    d = DatePoint(datetime.datetime(2018, 1, 1))
    assert d.value == datetime.datetime(2018, 1, 1)


def test_bitmex_process_points():
    p = BitMexProcessPoints(datetime.datetime(2018, 1, 1), datetime.datetime(2018, 1, 5))
    assert next(p).value == datetime.datetime(2018, 1, 1)
    assert next(p).value == datetime.datetime(2018, 1, 2)
    assert next(p).value == datetime.datetime(2018, 1, 3)
    assert next(p).value == datetime.datetime(2018, 1, 4)
    assert next(p).value == datetime.datetime(2018, 1, 5)

    with pytest.raises(StopIteration):
        next(p)

    p_list = list(p)
    assert p_list[0] == DatePoint(datetime.datetime(2018, 1, 1))
    assert p_list[1] == DatePoint(datetime.datetime(2018, 1, 2))
    assert p_list[2] == DatePoint(datetime.datetime(2018, 1, 3))
    assert p_list[3] == DatePoint(datetime.datetime(2018, 1, 4))
    assert p_list[4] == DatePoint(datetime.datetime(2018, 1, 5))

    p2 = BitMexProcessPoints(datetime.datetime(2018, 1, 1), datetime.datetime(2018, 1, 1))
    assert next(p2).value == datetime.datetime(2018, 1, 1)
    with pytest.raises(StopIteration):
        next(p2)
    p2_list = list(p2)
    assert p2_list[0] == DatePoint(datetime.datetime(2018, 1, 1))
    with pytest.raises(IndexError):
        p2_list[1]


def mkfile(filename):
    with open(filename, 'w') as f:
        f.write('1')


def random_quote_frame(length, timestamp=pandas.Timestamp(2018, 1, 3)):
    r = lambda: random.randint(1, 1000)  # noqa: E731

    df = pandas.DataFrame(
        [(timestamp, r(), r(), r(), r()) for i in range(length)],
        columns=['timestamp', "bidSize", "bidPrice", "askPrice", "askSize"])
    df.set_index('timestamp', inplace=True)
    return df


def random_trade_frame(length, timestamp=pandas.Timestamp(2018, 1, 3)):
    r = lambda: random.randint(1, 1000)  # noqa: E731

    columns = ["timestamp", "side", "size", "price", "tickDirection",
               "grossValue", "homeNotional", "foreignNotional"]
    df = pandas.DataFrame(
        [(timestamp, r(), r(), r(), r(), r(), r(), r()) for i in range(length)],
        columns=columns)
    df.set_index('timestamp', inplace=True)
    return df


def random_quote_hdf(path, length=3):
    tmp_df = random_quote_frame(length=length)
    tmp_df2 = random_quote_frame(length=length)

    tmp_df.to_hdf(path, '/XBTUSD',
                  data_columns=True, index=False, complib='blosc:blosclz',
                  complevel=9, append=True, format='table')
    tmp_df2.to_hdf(path, '/ETHUSD',
                   data_columns=True, index=False, complib='blosc:blosclz',
                   complevel=9, append=True, format='table')


def random_trade_hdf(path, length=3):
    tmp_df = random_trade_frame(length=length)
    tmp_df2 = random_trade_frame(length=length)

    tmp_df.to_hdf(path, '/XBTUSD',
                  data_columns=True, index=False, complib='blosc:blosclz',
                  complevel=9, append=True, format='table')
    tmp_df2.to_hdf(path, '/ETHUSD',
                   data_columns=True, index=False, complib='blosc:blosclz',
                   complevel=9, append=True, format='table')


def test_bitmex_downloader() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        b = BitMexDownloader(kind='quote', mode='csv', dst_dir=tmp)
        assert b.Streamer == QuoteZipFileStream
        assert b.start == START_DATE

    with tempfile.TemporaryDirectory() as tmp:
        mkfile(os.path.join(tmp, '20180103'))
        b = BitMexDownloader(kind='quote', mode='csv', dst_dir=tmp)
        assert b.Streamer == QuoteZipFileStream
        assert b.start == datetime.datetime(2018, 1, 4)

    with tempfile.TemporaryDirectory() as tmp:
        mkfile(os.path.join(tmp, '20180103'))
        b = BitMexDownloader(kind='trade', mode='csv', dst_dir=tmp)
        assert b.Streamer == TradeZipFileStream
        assert b.start == datetime.datetime(2018, 1, 4)

    with tempfile.TemporaryDirectory() as tmp:
        b = BitMexDownloader(kind='trade', mode='csv', dst_dir=tmp)
        assert b.Streamer == TradeZipFileStream
        assert b.start == START_DATE

    with tempfile.TemporaryDirectory() as tmp:
        b = BitMexDownloader(kind='instruments', mode='csv', dst_dir=tmp)
        assert b.Streamer == SymbolsStreamRequest
        assert b.start == b.end

    with tempfile.TemporaryDirectory() as tmp:
        b = BitMexDownloader(kind='trade', mode='tar', dst_dir=tmp)
        assert b.Streamer == TarStreamRequest
        assert b.start == START_DATE

    with tempfile.TemporaryDirectory() as tmp:
        mkfile(os.path.join(tmp, '20180103.csv.gz'))
        b = BitMexDownloader(kind='trade', mode='tar', dst_dir=tmp)
        assert b.Streamer == TarStreamRequest
        assert b.start == datetime.datetime(2018, 1, 4)

    with tempfile.TemporaryDirectory() as tmp:
        mkfile(os.path.join(tmp, '20180103.csv.gz'))
        b = BitMexDownloader(kind='quote', mode='tar', dst_dir=tmp)
        assert b.Streamer == TarStreamRequest
        assert b.start == datetime.datetime(2018, 1, 4)

    with tempfile.TemporaryDirectory() as tmp:
        b = BitMexDownloader(kind='quote', mode='tar', dst_dir=tmp)
        assert b.Streamer == TarStreamRequest
        assert b.start == START_DATE

    with tempfile.TemporaryDirectory() as tmp:
        b = BitMexDownloader(kind='trade', mode='hdf', dst_dir=tmp)
        assert b.Streamer == HDFTradeStream
        assert b.start == START_DATE

    with tempfile.TemporaryDirectory() as tmp:
        b = BitMexDownloader(kind='quote', mode='hdf', dst_dir=tmp)
        assert b.Streamer == HDFQuoteStream
        assert b.start == START_DATE

    with tempfile.TemporaryDirectory() as tmp:
        random_quote_hdf(os.path.join(tmp, 'quote.hdf'))
        b = BitMexDownloader(kind='quote', mode='hdf', dst_dir=tmp)
        assert b.Streamer == HDFQuoteStream
        assert b.start == datetime.datetime(2018, 1, 4)

    with tempfile.TemporaryDirectory() as tmp:
        random_trade_hdf(os.path.join(tmp, 'trade.hdf'))
        b = BitMexDownloader(kind='trade', mode='hdf', dst_dir=tmp)
        assert b.Streamer == HDFTradeStream
        assert b.start == datetime.datetime(2018, 1, 4)


def test_bitmexdownloader_do_all():
    with tempfile.TemporaryDirectory() as tmp:
        start = datetime.datetime.utcnow() + relativedelta(days=-2, hour=0, minute=0, second=0, microsecond=0)
        mkfile(os.path.join(tmp, start.strftime('%Y%m%d')))
        b = BitMexDownloader(kind='trade', mode='csv', dst_dir=tmp)
        m = MagicMock()
        b.Streamer = m
        b.do_all()
        stream = m()
        stream.process.assert_called_once_with()

        b = BitMexDownloader(kind='trade', mode='csv', dst_dir=tmp)
        m = MagicMock(side_effect=DataDownloadError())
        b.Streamer = m
        b.do_all()

        with pytest.raises(KeyError):
            b = BitMexDownloader(kind='trade', mode='csv', dst_dir=tmp)
            m = MagicMock(side_effect=KeyError())
            b.Streamer = m
            b.do_all()


class MockRawStreamRequest(TarStreamRequest):
    def __init__(self, *args, **kwargs):
        self._stream = kwargs.pop('stream', '')
        super(MockRawStreamRequest, self).__init__(*args, **kwargs)

    _stream_requests = _mock_stream


class MockTradeZipFileStream(TradeZipFileStream):
    def __init__(self, *args, **kwargs):
        self._stream = kwargs.pop('stream', '')
        super(MockTradeZipFileStream, self).__init__(*args, **kwargs)

    _stream_requests = _mock_stream


class MockQuoteZipFileStream(QuoteZipFileStream):
    def __init__(self, *args, **kwargs):
        self._stream = kwargs.pop('stream', '')
        super(MockQuoteZipFileStream, self).__init__(*args, **kwargs)

    _stream_requests = _mock_stream


class MockSymbolsStream(SymbolsStreamRequest):
    def __init__(self, *args, **kwargs):
        self._stream = kwargs.pop('stream', '')
        super(SymbolsStreamRequest, self).__init__(*args, **kwargs)

    _stream_requests = _mock_stream


def test_symbols_stream_request():
    with tempfile.TemporaryDirectory() as tmp:
        stream = MockSymbolsStream(mock_url, tmp, stream=stream_symbols)
        stream.process()

        with open(os.path.join(tmp, INSTRUMENT_FILENAME), 'rb') as f:
            content = f.read()

        assert content == stream_symbols


def test_raw_stream_request():
    with tempfile.TemporaryDirectory() as tmp:
        date = datetime.datetime(2018, 1, 1)
        outcome = os.path.join(tmp, date.strftime("%Y%m%d") + '.csv.gz')
        stream = MockRawStreamRequest(date, mock_url, tmp, stream=stream_b)
        stream.process()

        with open(outcome, 'rb') as f:
            content = f.read()

        assert content == stream_b


def test_raw_stream_request_exception():
    with tempfile.TemporaryDirectory() as tmp:
        date = datetime.datetime(2018, 1, 1)
        outcome = os.path.join(tmp, date.strftime("%Y%m%d") + '.csv.gz')
        stream = MockRawStreamRequest(date, mock_url, tmp, stream=stream_b)
        stream._stream_requests = _mock_exception_stream
        with pytest.raises(DataDownloadError):
            stream.process()

        assert not os.path.exists(outcome)


def test_trade_zip_file_stream():
    d = datetime.datetime(2018, 1, 1)

    with tempfile.TemporaryDirectory() as tmp:
        tar_dir = os.path.join(tmp, d.strftime("%Y%m%d"))

        stream = MockTradeZipFileStream(date=d, url=mock_url, dst_dir=tmp, stream=stream_trade)

        stream.process()

        with gzip.open(os.path.join(tar_dir, "ADAZ18.csv.gz")) as f:
            content = f.read()
            assert content == b"""timestamp,symbol,side,size,price,tickDirection,trdMatchID,grossValue,homeNotional,foreignNotional
2018-12-05D00:00:25.948313000,ADAZ18,Sell,166774,9.54e-06,MinusTick,498350a3-8c03-affd-cf87-e6d8a90b70e5,159102396,166774,1.591024
"""
        with gzip.open(os.path.join(tar_dir, "XBTUSD.csv.gz")) as f:
            content = f.read()
            assert content == b"""timestamp,symbol,side,size,price,tickDirection,trdMatchID,grossValue,homeNotional,foreignNotional
2018-12-05D00:00:25.948313000,XBTUSD,Sell,11,9.54e-06,ZeroMinusTick,1d004a95-44fa-c75c-47cd-d651ecd41c25,10494,11,0.00010494
"""

        with gzip.open(os.path.join(tar_dir, "XBTZ18.csv.gz")) as f:
            content = f.read()
            assert content == b"""timestamp,symbol,side,size,price,tickDirection,trdMatchID,grossValue,homeNotional,foreignNotional
2018-12-05D00:00:25.948313000,XBTZ18,Sell,10000,9.54e-06,ZeroMinusTick,214aa626-cb6a-054f-ccf5-da4e14b5fd23,9540000,10000,0.0954
"""


def test_trade_zip_file_stream_exception():
    d = datetime.datetime(2018, 1, 1)

    with tempfile.TemporaryDirectory() as tmp:
        tar_dir = os.path.join(tmp, d.strftime("%Y%m%d"))

        stream = MockTradeZipFileStream(date=d, url=mock_url, dst_dir=tmp, stream=stream_trade)
        stream._stream_requests = _mock_exception_stream

        with pytest.raises(DataDownloadError):
            stream.process()

        assert not os.path.exists(tar_dir)


def test_quote_zip_file_stream():
    d = datetime.datetime(2018, 1, 1)

    with tempfile.TemporaryDirectory() as tmp:
        tar_dir = os.path.join(tmp, d.strftime("%Y%m%d"))

        stream = MockQuoteZipFileStream(date=d, url=mock_url, dst_dir=tmp, stream=stream_quote)

        stream.process()

        with gzip.open(os.path.join(tar_dir, "ADAZ18.csv.gz")) as f:
            content = f.read()
            assert content == b"""timestamp,symbol,bidSize,bidPrice,askPrice,askSize
2018-12-05D00:00:04.778522000,ADAZ18,256089,9.54e-06,9.55e-06,524060
"""
        with gzip.open(os.path.join(tar_dir, "XBTUSD.csv.gz")) as f:
            content = f.read()
            assert content == b"""timestamp,symbol,bidSize,bidPrice,askPrice,askSize
2018-12-05D00:00:05.045590000,XBTUSD,256081,9.54e-06,9.55e-06,544060
"""

        with gzip.open(os.path.join(tar_dir, "XBTZ18.csv.gz")) as f:
            content = f.read()
            assert content == b"""timestamp,symbol,bidSize,bidPrice,askPrice,askSize
2018-12-05D00:00:07.302458000,XBTZ18,256083,9.54e-06,9.55e-06,574060
"""


def test_quote_zip_file_stream_exception():
    d = datetime.datetime(2018, 1, 1)

    with tempfile.TemporaryDirectory() as tmp:
        tar_dir = os.path.join(tmp, d.strftime("%Y%m%d"))

        stream = MockQuoteZipFileStream(date=d, url=mock_url, dst_dir=tmp, stream=stream_quote)
        stream._stream_requests = _mock_exception_stream

        with pytest.raises(DataDownloadError):
            stream.process()

        assert not os.path.exists(tar_dir)


def test_quote_hdf_stream():
    point = DatePoint(datetime.datetime(2018, 1, 3))

    with patch("MonkTrader.exchange.bitmex.data.download.requests") as m:
        resp = m.get()
        resp.raw = io.BytesIO(stream_quote_gzip)
        with tempfile.TemporaryDirectory() as tmp:
            stream = HDFQuoteStream('test_url', tmp, point=point)
            stream.process()

            with pandas.HDFStore(os.path.join(tmp, 'quote.hdf'), 'r') as store:
                XBTz18 = store['XBTZ18']

                assert XBTz18['bidSize'][0] == 256083
                assert XBTz18['bidPrice'][0] == 9.54e-06
                assert XBTz18['askPrice'][0] == 9.55e-06
                assert XBTz18['askSize'][0] == 574060

                XBTUSD = store['XBTUSD']

                assert XBTUSD['bidSize'][0] == 256081
                assert XBTUSD['bidPrice'][0] == 9.54e-06
                assert XBTUSD['askPrice'][0] == 9.55e-06
                assert XBTUSD['askSize'][0] == 544060

                ADAZ18 = store['ADAZ18']

                assert ADAZ18['bidSize'][0] == 256089
                assert ADAZ18['bidPrice'][0] == 9.54e-06
                assert ADAZ18['askPrice'][0] == 9.55e-06
                assert ADAZ18['askSize'][0] == 524060


def test_quote_hdf_stream_exception():
    d = datetime.datetime(2018, 1, 5)
    point = DatePoint(d)

    with tempfile.TemporaryDirectory() as tmp:
        random_quote_hdf(os.path.join(tmp, 'quote.hdf'), 4)
        stream = HDFTradeStream('test_url', tmp, point=point)
        append = random_quote_frame(3, d)
        with pytest.raises(DataDownloadError):
            with patch("MonkTrader.exchange.bitmex.data.download.read_quote_tar"):
                with patch("MonkTrader.exchange.bitmex.data.download.requests"):
                    with patch("MonkTrader.exchange.bitmex.data.download.classify_df") as f:
                        f.items.return_value = [
                            ("XBTUSD", append),
                            ("ETHUSD", 's')]
                    stream.process()

        with pandas.HDFStore(os.path.join(tmp, 'quote.hdf'), 'r') as store:
            XBT = store['XBTUSD']
            assert len(XBT) == 4


def test_trade_hdf_stream_exception():
    d = datetime.datetime(2018, 1, 5)
    point = DatePoint(d)
    with tempfile.TemporaryDirectory() as tmp:
        random_trade_hdf(os.path.join(tmp, 'trade.hdf'), 4)

        stream = HDFTradeStream('test_url', tmp, point=point)
        append = random_trade_frame(3, d)
        with pytest.raises(DataDownloadError):
            with patch("MonkTrader.exchange.bitmex.data.download.read_trade_tar"):
                with patch("MonkTrader.exchange.bitmex.data.download.requests"):
                    with patch("MonkTrader.exchange.bitmex.data.download.classify_df") as f:
                        f().items.return_value = [
                            ("XBTUSD", append),
                            ("ETHUSD", 's')]
                        stream.process()

        with pandas.HDFStore(os.path.join(tmp, 'trade.hdf'), 'r') as store:
            XBT = store['XBTUSD']
            assert len(XBT) == 4


def test_trade_hdf_stream():
    point = DatePoint(datetime.datetime(2018, 1, 3))

    with patch("MonkTrader.exchange.bitmex.data.download.requests") as m:
        resp = m.get()
        resp.raw = io.BytesIO(stream_trade_gzip)
        with tempfile.TemporaryDirectory() as tmp:
            stream = HDFTradeStream('test_url', tmp, point=point)
            stream.process()

            with pandas.HDFStore(os.path.join(tmp, 'trade.hdf'), 'r') as store:
                XBTz18 = store['XBTZ18']

                assert XBTz18['side'][0] == SIDE.SELL.value
                assert XBTz18['size'][0] == 10000
                assert XBTz18['price'][0] == 9.54e-06
                assert XBTz18['tickDirection'][0] == TICK_DIRECTION.ZERO_MINUS_TICK.value
                assert XBTz18['grossValue'][0] == 9540000
                assert XBTz18['homeNotional'][0] == 10000
                assert XBTz18['foreignNotional'][0] == 0.0954

                ADAZ18 = store['ADAZ18']

                assert ADAZ18['side'][0] == SIDE.SELL.value
                assert ADAZ18['size'][0] == 166774
                assert ADAZ18['price'][0] == 9.54e-06
                assert ADAZ18['tickDirection'][0] == TICK_DIRECTION.MINUS_TICK.value
                assert ADAZ18['grossValue'][0] == 159102396
                assert ADAZ18['homeNotional'][0] == 166774
                assert ADAZ18['foreignNotional'][0] == 1.591024

                XBTUSD = store['XBTUSD']

                assert XBTUSD['side'][0] == SIDE.SELL.value
                assert XBTUSD['size'][0] == 11
                assert XBTUSD['price'][0] == 9.54e-06
                assert XBTUSD['tickDirection'][0] == TICK_DIRECTION.ZERO_MINUS_TICK.value
                assert XBTUSD['grossValue'][0] == 10494
                assert XBTUSD['homeNotional'][0] == 11
                assert XBTUSD['foreignNotional'][0] == 0.00010494
