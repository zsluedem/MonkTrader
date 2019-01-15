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
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from MonkTrader.assets.positions import PositionManager, BasePosition, FutureBasePosition, DIRECTION, \
    FutureCrossIsolatePosition, IsolatedPosition, CrossPosition, POSITION_EFFECT
from MonkTrader.assets.order import BaseOrder
from MonkTrader.assets.trade import Trade
from MonkTrader.exception import MarginNotEnoughException, MarginException
from unittest.mock import MagicMock, PropertyMock, patch
from ..utils import random_string
import pytest


def test_position_manager(instrument, base_account):
    position_manager = PositionManager(BasePosition, base_account)
    position = position_manager[instrument]
    assert isinstance(position, BasePosition)
    assert position is position_manager[instrument]


def test_empty_position_deal(instrument, base_account):
    position = BasePosition(instrument=instrument, account=base_account)
    order = BaseOrder(account=base_account, order_id=random_string(6), instrument=instrument, quantity=80)
    # open a position
    trade1 = Trade(order=order, exec_price=10, exec_quantity=30, trade_id=random_string(6))
    assert position.position_effect(trade1) == POSITION_EFFECT.OPEN
    position.deal(trade1)
    assert position.quantity == 30
    assert position.open_price == trade1.avg_price

    # get more on a position
    trade2 = Trade(order=order, exec_price=13, exec_quantity=50, trade_id=random_string(6))
    position.deal(trade2)
    assert position.position_effect(trade2) == POSITION_EFFECT.GET_MORE
    new_open_price = (trade1.avg_price * trade1.exec_quantity + trade2.avg_price * trade2.exec_quantity) / (
            trade1.exec_quantity + trade2.exec_quantity)
    assert position.quantity == 80
    assert position.open_price == new_open_price

    # sell part of the position
    order2 = BaseOrder(account=base_account, order_id=random_string(6), instrument=instrument, quantity=-180)
    trade3 = Trade(order=order2, exec_price=15, exec_quantity=-40, trade_id=random_string(6))
    assert position.position_effect(trade3) == POSITION_EFFECT.CLOSE_PART
    position.deal(trade3)
    assert position.quantity == 40
    assert position.open_price == new_open_price

    # close a position and open a opposite position
    trade4 = Trade(order=order2, exec_price=15, exec_quantity=-60, trade_id=random_string(6))
    assert position.position_effect(trade4) == POSITION_EFFECT.CLOSE_AND_OPEN
    position.deal(trade4)
    assert position.quantity == -20
    assert position.open_price == trade4.avg_price

    # get more on a position
    trade5 = Trade(order=order2, exec_price=12, exec_quantity=-80, trade_id=random_string(6))
    assert position.position_effect(trade5) == POSITION_EFFECT.GET_MORE
    position.deal(trade5)
    assert position.quantity == -100
    assert position.open_price == (-20 * trade4.avg_price + trade5.exec_quantity * trade5.avg_price) / (
            -20 + trade5.exec_quantity)

    # close a position
    order3 = BaseOrder(account=base_account, order_id=random_string(6), instrument=instrument, quantity=100)
    trade6 = Trade(order=order3, exec_price=12, exec_quantity=100, trade_id=random_string(6))
    assert position.position_effect(trade6) == POSITION_EFFECT.CLOSE
    position.deal(trade6)
    assert position.quantity == 0
    assert position.open_price == 0

    # open a position
    order4 = BaseOrder(account=base_account, order_id=random_string(6), instrument=instrument, quantity=-80)
    trade7 = Trade(order=order4, exec_price=13, exec_quantity=-30, trade_id=random_string(6))
    assert position.position_effect(trade7) == POSITION_EFFECT.OPEN
    position.deal(trade7)
    assert position.quantity == -30
    assert position.open_price == trade7.avg_price

    # get more on position
    trade8 = Trade(order=order4, exec_price=15, exec_quantity=-50, trade_id=random_string(6))
    assert position.position_effect(trade8) == POSITION_EFFECT.GET_MORE
    position.deal(trade8)
    new_open_price2 = (trade7.avg_price * trade7.exec_quantity + trade8.avg_price * trade8.exec_quantity) / (
            trade7.exec_quantity + trade8.exec_quantity)
    assert position.quantity == -80
    assert position.open_price == new_open_price2

    # sell part of the position
    order5 = BaseOrder(account=base_account, order_id=random_string(6), instrument=instrument, quantity=180)
    trade9 = Trade(order=order5, exec_price=10, exec_quantity=40, trade_id=random_string(6))
    assert position.position_effect(trade9) == POSITION_EFFECT.CLOSE_PART
    position.deal(trade9)
    assert position.quantity == -40
    assert position.open_price == new_open_price2

    # close a position and open a opposite position
    trade10 = Trade(order=order5, exec_price=11, exec_quantity=60, trade_id=random_string(6))
    assert position.position_effect(trade10) == POSITION_EFFECT.CLOSE_AND_OPEN
    position.deal(trade10)
    assert position.quantity == 20
    assert position.open_price == trade10.avg_price

    # get more on a position
    trade11 = Trade(order=order5, exec_price=13, exec_quantity=80, trade_id=random_string(6))
    assert position.position_effect(trade11) == POSITION_EFFECT.GET_MORE
    position.deal(trade11)
    assert position.quantity == 100
    assert position.open_price == (20 * trade10.avg_price + trade11.avg_price * trade11.exec_quantity) / (
            trade11.exec_quantity + 20)

    # close a position
    order6 = BaseOrder(account=base_account, order_id=random_string(6), instrument=instrument, quantity=-100)
    trade12 = Trade(order=order6, exec_price=15, exec_quantity=-100, trade_id=random_string(6))
    assert position.position_effect(trade12) == POSITION_EFFECT.CLOSE
    position.deal(trade12)
    assert position.quantity == 0
    assert position.open_price == 0


def test_future_base_position(exchange, future_instrument, future_account):
    exchange.get_last_price.return_value = 10
    assert exchange == future_instrument.exchange
    assert future_instrument.last_price == 10
    position = FutureBasePosition(instrument=future_instrument, account=future_account)

    position.quantity = 100
    position.open_price = 9.5
    assert position.direction == DIRECTION.LONG
    assert position.market_value == 1000
    assert position.open_value == 950
    assert position.unrealised_pnl == 47.5
    assert position.min_open_maint_margin == 23.75
    assert position.open_init_margin == 47.5
    assert position.last_init_margin == 50
    assert position.min_last_maint_margin == 25

    position.quantity = 100
    position.open_price = 11
    assert position.direction == DIRECTION.LONG
    assert position.market_value == 1000
    assert position.open_value == 1100
    assert position.unrealised_pnl == -102.5
    assert position.min_open_maint_margin == 27.5
    assert position.open_init_margin == 55
    assert position.last_init_margin == 50
    assert position.min_last_maint_margin == 25

    position.quantity = -100
    position.open_price = 9
    assert position.direction == DIRECTION.SHORT
    assert position.market_value == 1000
    assert position.open_value == 900
    assert position.unrealised_pnl == -102.5
    assert position.min_open_maint_margin == 22.5
    assert position.open_init_margin == 45
    assert position.last_init_margin == 50
    assert position.min_last_maint_margin == 25

    position.quantity = -100
    position.open_price = 11
    assert position.direction == DIRECTION.SHORT
    assert position.market_value == 1000
    assert position.open_value == 1100
    assert position.unrealised_pnl == 97.5
    assert position.min_open_maint_margin == 27.5
    assert position.open_init_margin == 55
    assert position.last_init_margin == 50
    assert position.min_last_maint_margin == 25


def test_cross_position(exchange, future_instrument, future_account):
    exchange.get_last_price.return_value = 18
    assert future_instrument.last_price == 18

    future_account = MagicMock(future_account)
    future_account.available_balance = 10000

    position = CrossPosition(instrument=future_instrument, account=future_account)
    # long
    position.open_price = 20
    position.quantity = 2000
    assert position.liq_price == pytest.approx(14.3958, 0.0001)
    assert position.bankruptcy_price == pytest.approx(14.0351, 0.0001)
    assert position.maint_margin == 12000
    assert position.position_margin == pytest.approx(1890)
    with pytest.raises(MarginException):
        position.maint_margin = 10
    with pytest.raises(MarginException):
        position.leverage

    # short
    future_account.available_balance = 12000
    position.open_price = 22
    position.quantity = -1800
    assert position.liq_price == pytest.approx(28.9699, 0.0001)
    assert position.bankruptcy_price == pytest.approx(29.6924, 0.0001)
    assert position.maint_margin == 13980
    assert position.position_margin == pytest.approx(1701)
    with pytest.raises(MarginException):
        position.maint_margin = 10
    with pytest.raises(MarginException):
        position.leverage


def test_isolated_position(exchange, future_instrument, future_account):
    exchange.get_last_price.return_value = 10
    assert future_instrument.last_price == 10

    future_account = MagicMock(future_account)
    future_account.available_balance = 1000
    assert future_account.available_balance == 1000

    position = IsolatedPosition(instrument=future_instrument, account=future_account)

    # long
    position.open_price = 11
    position.quantity = 1000
    position.maint_margin = 800
    assert position.leverage == 12.5
    assert position.liq_price == pytest.approx(10.4884, 0.0001)
    assert position.position_margin == 800
    assert position.bankruptcy_price == pytest.approx(10.2255, 0.0001)

    with pytest.raises(MarginNotEnoughException):
        # more than the available margin
        position.maint_margin = 1100

    with pytest.raises(MarginNotEnoughException):
        # less than the init margin
        position.maint_margin = 400

    with pytest.raises(MarginNotEnoughException):
        # more than the available margin
        position.set_leverage(2)

    future_account.available_balance = 10000
    position.open_price = 11
    position.quantity = 1000
    position.set_leverage(5)
    assert position.maint_margin == 2000
    assert position.leverage == 5
    assert position.liq_price == pytest.approx(9.2544, 0.0001)
    assert position.position_margin == 2000
    assert position.bankruptcy_price == pytest.approx(9.0225, 0.0001)

    # short
    future_account.available_balance = 10000
    exchange.get_last_price.return_value = 11

    assert future_instrument.last_price == 11
    position.maint_margin = 1000
    position.open_price = 9
    position.quantity = -600
    assert position.liq_price == pytest.approx(10.3811, 0.0001)
    assert position.position_margin == 1000
    assert position.bankruptcy_price == pytest.approx(10.6401, 0.0001)
    assert position.leverage == 6.6
    # position.maint_margin =
    with pytest.raises(MarginNotEnoughException):
        # more than the available margin
        position.maint_margin = 11000

    with pytest.raises(MarginNotEnoughException):
        # less than the init margin
        position.maint_margin = 100

    with pytest.raises(MarginNotEnoughException):
        future_account.available_balance = 3000
        position.set_leverage(2)

    future_account.available_balance = 10000
    exchange.get_last_price.return_value = 11
    assert future_instrument.last_price == 11
    position.open_price = 10.5
    position.quantity = -800

    position.set_leverage(4)
    assert position.maint_margin == 2200
    assert position.leverage == 4
    assert position.position_margin == 2200
    assert position.liq_price == pytest.approx(12.8953, 0.0001)
    assert position.bankruptcy_price == pytest.approx(13.2169, 0.0001)


def test_cross_isolated_position(exchange, future_instrument, future_account):
    exchange.get_last_price.return_value = 18
    assert future_instrument.last_price == 18

    future_account = MagicMock(future_account)
    future_account.available_balance = 10000
    assert future_account.available_balance == 10000

    position = FutureCrossIsolatePosition(instrument=future_instrument, account=future_account)
    position.open_price = 20
    position.quantity = 2000
    assert position.isolated == False
    assert position.is_isolated == False
    assert position.liq_price == pytest.approx(14.3958, 0.0001)
    assert position.bankruptcy_price == pytest.approx(14.0351, 0.0001)
    assert position.maint_margin == 12000
    assert position.position_margin == pytest.approx(1890)
    with pytest.raises(MarginException):
        position.leverage
    with pytest.raises(MarginException):
        position.maint_margin = 100

    with pytest.raises(MarginNotEnoughException):
        position.set_leverage(3)
    assert position.isolated == False
    with pytest.raises(MarginNotEnoughException):
        position.set_maint_margin(300)
    assert position.isolated == False

    position.set_leverage(4)
    assert position.isolated == True
    assert position.is_isolated == True
    assert position.maint_margin == 9000
    assert position.liq_price == pytest.approx(15.9383, 0.0001)
    assert position.bankruptcy_price == pytest.approx(15.5388, 0.0001)
    assert position.position_margin == 9000
    assert position.leverage == 4

    position.set_cross()
    assert position.isolated == False
    assert position.is_isolated == False

    position.maint_margin = 9000
    assert position.isolated == True
    assert position.is_isolated == True
    assert position.liq_price == pytest.approx(15.9383, 0.0001)
    assert position.bankruptcy_price == pytest.approx(15.5388, 0.0001)

    position.set_cross()
    assert position.isolated == False
    assert position.is_isolated == False
    assert position.liq_price == pytest.approx(14.3958, 0.0001)
    assert position.bankruptcy_price == pytest.approx(14.0351, 0.0001)

    position.set_maint_margin(9000)
    assert position.isolated == True
    assert position.is_isolated == True
