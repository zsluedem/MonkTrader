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
import pytest
from unittest.mock import MagicMock, patch

from dateutil.tz import tzutc
from MonkTrader.assets.instrument import (
    DownsideInstrument, FutureInstrument, PerpetualInstrument,
    UpsideInstrument,
)
from MonkTrader.exchange.bitmex.data.loader import BitmexDataloader
from MonkTrader.utils.timefunc import utc_datetime
from tests.tools import get_resource_path


def test_bitmex_dataloader_instruments(exchange: MagicMock) -> None:
    context = MagicMock()
    dataloader = BitmexDataloader(exchange, context, get_resource_path('bitmex'))
    dataloader.load_instruments()

    XBT7D_D95 = dataloader.instruments.get('XBT7D_D95')

    # detailed values see file instruments.json in resource
    assert isinstance(XBT7D_D95, DownsideInstrument)
    assert XBT7D_D95.listing_date == datetime.datetime(2018, 12, 28, 12, tzinfo=tzutc())
    assert XBT7D_D95.expiry_date == datetime.datetime(2019, 1, 4, 12, tzinfo=tzutc())
    assert XBT7D_D95.underlying == "XBT"
    assert XBT7D_D95.quote_currency == "XBT"
    assert XBT7D_D95.lot_size == 1
    assert XBT7D_D95.tick_size == .00001
    assert XBT7D_D95.maker_fee == 0
    assert XBT7D_D95.taker_fee == 0
    assert XBT7D_D95.exchange == exchange
    assert XBT7D_D95.root_symbol == 'XBT'
    assert XBT7D_D95.init_margin_rate == 1
    assert XBT7D_D95.maint_margin_rate == 0
    assert XBT7D_D95.settlement_fee == 0
    assert XBT7D_D95.settle_currency == "XBt"
    assert XBT7D_D95.settle_date == datetime.datetime(2019, 1, 4, 12, tzinfo=tzutc())
    assert XBT7D_D95.front_date == datetime.datetime(2018, 12, 28, 12, tzinfo=tzutc())
    assert XBT7D_D95.reference_symbol == ".BXBT30M"
    assert XBT7D_D95.deleverage

    XBT7D_U105 = dataloader.instruments.get('XBT7D_U105')

    # detailed values see file instruments.json in resource
    assert isinstance(XBT7D_U105, UpsideInstrument)
    assert XBT7D_U105.listing_date == datetime.datetime(2018, 12, 28, 12, tzinfo=tzutc())
    assert XBT7D_U105.expiry_date == datetime.datetime(2019, 1, 4, 12, tzinfo=tzutc())
    assert XBT7D_U105.underlying == "XBT"
    assert XBT7D_U105.quote_currency == "XBT"
    assert XBT7D_U105.lot_size == 1
    assert XBT7D_U105.tick_size == .00001
    assert XBT7D_U105.maker_fee == 0
    assert XBT7D_U105.taker_fee == 0
    assert XBT7D_U105.exchange == exchange
    assert XBT7D_U105.root_symbol == 'XBT'
    assert XBT7D_U105.init_margin_rate == 1
    assert XBT7D_U105.maint_margin_rate == 0
    assert XBT7D_U105.settlement_fee == 0
    assert XBT7D_U105.settle_currency == "XBt"
    assert XBT7D_U105.settle_date == datetime.datetime(2019, 1, 4, 12, tzinfo=tzutc())
    assert XBT7D_U105.front_date == datetime.datetime(2018, 12, 28, 12, tzinfo=tzutc())
    assert XBT7D_U105.reference_symbol == ".BXBT30M"
    assert XBT7D_U105.deleverage

    XBTUSD = dataloader.instruments.get('XBTUSD')

    # detailed values see file instruments.json in resource
    assert isinstance(XBTUSD, PerpetualInstrument)
    assert XBTUSD.listing_date == datetime.datetime(2016, 5, 4, 12, tzinfo=tzutc())
    assert XBTUSD.expiry_date is None
    assert XBTUSD.underlying == "XBT"
    assert XBTUSD.quote_currency == "USD"
    assert XBTUSD.lot_size == 1
    assert XBTUSD.tick_size == .5
    assert XBTUSD.maker_fee == -0.00025
    assert XBTUSD.taker_fee == 0.00075
    assert XBTUSD.exchange == exchange
    assert XBTUSD.root_symbol == 'XBT'
    assert XBTUSD.init_margin_rate == 0.01
    assert XBTUSD.maint_margin_rate == 0.005
    assert XBTUSD.settlement_fee == 0
    assert XBTUSD.settle_currency == "XBt"
    assert XBTUSD.settle_date is None
    assert XBTUSD.front_date == datetime.datetime(2016, 5, 4, 12, tzinfo=tzutc())
    assert XBTUSD.reference_symbol == ".BXBT"
    assert XBTUSD.deleverage

    TRXH19 = dataloader.instruments.get('TRXH19')

    # detailed values see file instruments.json in resource
    assert isinstance(TRXH19, FutureInstrument)
    assert TRXH19.listing_date == datetime.datetime(2018, 12, 12, 6, tzinfo=tzutc())
    assert TRXH19.expiry_date == datetime.datetime(2019, 3, 29, 12, tzinfo=tzutc())
    assert TRXH19.underlying == "TRX"
    assert TRXH19.quote_currency == "XBT"
    assert TRXH19.lot_size == 1
    assert TRXH19.tick_size == 1e-8
    assert TRXH19.maker_fee == -0.0005
    assert TRXH19.taker_fee == 0.0025
    assert TRXH19.exchange == exchange
    assert TRXH19.root_symbol == 'TRX'
    assert TRXH19.init_margin_rate == 0.05
    assert TRXH19.maint_margin_rate == 0.025
    assert TRXH19.settlement_fee == 0
    assert TRXH19.settle_currency == "XBt"
    assert TRXH19.settle_date == datetime.datetime(2019, 3, 29, 12, tzinfo=tzutc())
    assert TRXH19.front_date == datetime.datetime(2019, 2, 22, 12, tzinfo=tzutc())
    assert TRXH19.reference_symbol == ".TRXXBT30M"
    assert TRXH19.deleverage


def test_bitmex_dataloader_kline_data(exchange: MagicMock) -> None:
    context = MagicMock()
    with patch("MonkTrader.exchange.bitmex.data.loader.KLINE_FILE_NAME", 'test_table.hdf'):
        dataloader = BitmexDataloader(exchange, context, get_resource_path())

        instrument = MagicMock()
        instrument.symbol = "XBTZ15"
        context.now = utc_datetime(2015, 12, 25, 11, 40)

        assert dataloader.get_last_price(instrument) == 454.00
        kline_df = dataloader.get_kline(instrument, 50)
        assert len(kline_df) == 50
        assert kline_df.index[-1] == utc_datetime(2015, 12, 25, 11, 39)

        context.now = utc_datetime(2016, 1, 1, 11, 12)

        assert dataloader.get_last_price(instrument) == 0
