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
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Type

from monkq.assets.const import DIRECTION, POSITION_EFFECT, SIDE
from monkq.assets.instrument import FutureInstrument
from monkq.assets.order import FutureLimitOrder
from monkq.assets.positions import (
    BasePosition, FuturePosition, PositionManager,
)
from monkq.assets.trade import Trade
from monkq.exchange.base import BaseSimExchange


@dataclass()
class APIKey():
    api_secret: str
    api_key: str


@dataclass()
class BaseAccount():
    exchange: BaseSimExchange
    position_cls: Type[BasePosition]
    positions: PositionManager = field(init=False)
    wallet_balance: float = 0

    def __post_init__(self) -> None:
        self.positions = PositionManager(self.position_cls, self)

    def deal(self, trade: Trade) -> None:
        raise NotImplementedError()

    @property
    def total_capital(self) -> float:
        return self.wallet_balance

    def __getstate__(self) -> dict:
        return {
            "exchange": self.exchange,
            "exchange_name": self.exchange.name,
            "exchange_settings": self.exchange.exchange_setting,
            "position_cls": self.position_cls,
            "positions": list(self.positions.items()),
            "wallet_balance": self.wallet_balance
        }

    def __setstate__(self, state: dict) -> None:
        self.exchange = state['exchange']  # type:ignore
        # self.exchange = ExchangePickle()  # type:ignore
        self.exchange.name = state['exchange_name']
        self.exchange.exchange_setting = state['exchange_settings']
        self.wallet_balance = state['wallet_balance']
        self.positions = {}  # type:ignore
        for key, value in state['positions']:
            self.positions[key] = value


@dataclass()
class RealFutureAccount(BaseAccount):
    api_key: APIKey = APIKey('', '')


@dataclass()
class FutureAccount(BaseAccount):
    position_cls: Type[BasePosition] = FuturePosition

    @property
    def position_margin(self) -> float:
        return sum([position.position_margin for instrument, position in self.positions.items()])

    @property
    def order_margin(self) -> float:
        """
        Not that simple
        :return:
        """
        d: Dict[FutureInstrument, List[FutureLimitOrder]] = defaultdict(list)
        for order in self.exchange.get_open_orders(self):
            if isinstance(order, FutureLimitOrder):
                d[order.instrument].append(order)
        return sum([self._order_margin(instrument, orders) for instrument, orders in d.items()])

    def _order_margin(self, instrument: FutureInstrument, orders: List[FutureLimitOrder]) -> float:
        """
        :param instrument:
        :param orders:
        :return:
        """
        init_rate: float
        position = self.positions[instrument]
        if position.isolated:
            init_rate = 1 / position.leverage
        else:
            init_rate = instrument.init_margin_rate
        long_value: float = 0.
        short_value: float = 0.

        opposite_orders: List[FutureLimitOrder] = []
        for order in orders:
            if order.side == SIDE.BUY:
                long_value += order.remain_value
            else:
                short_value += order.remain_value
            if order.direction != position.direction:
                opposite_orders.append(order)

        opposite_orders = sorted(opposite_orders, key=lambda x: x.price)

        quantity: float = 0
        opposite_offset_value: float = 0
        for order in opposite_orders:
            if position.direction == DIRECTION.LONG:
                if quantity - order.remain_quantity < position.quantity:
                    opposite_offset_value += order.remain_value
                    quantity -= order.remain_quantity
                else:
                    valid_quantity = position.quantity - quantity
                    opposite_offset_value += valid_quantity * order.price
                    break
            else:
                if quantity - order.remain_quantity > position.quantity:
                    opposite_offset_value += order.remain_value
                    quantity -= order.remain_quantity
                else:
                    valid_quantity = quantity - position.quantity
                    opposite_offset_value += valid_quantity * order.price
                    break

        if position.direction == DIRECTION.LONG:
            short_value -= opposite_offset_value
        else:
            long_value -= opposite_offset_value

        valid_value: float = max(short_value, long_value)

        return valid_value * (init_rate + 2 * instrument.taker_fee)

    @property
    def unrealised_pnl(self) -> float:
        return sum([position.unrealised_pnl for instrument, position in self.positions.items()])

    @property
    def margin_balance(self) -> float:
        return self.wallet_balance + self.unrealised_pnl

    @property
    def total_capital(self) -> float:
        return self.margin_balance

    @property
    def available_balance(self) -> float:
        return self.margin_balance - self.order_margin - self.position_margin

    def deal(self, trade: Trade) -> None:
        position = self.positions[trade.instrument]
        position_effect = position.position_effect(trade)

        if position_effect == POSITION_EFFECT.OPEN or position_effect == POSITION_EFFECT.GET_MORE:
            pass
        else:
            if position_effect == POSITION_EFFECT.CLOSE or position_effect == POSITION_EFFECT.CLOSE_PART:
                profit_quantity = abs(trade.exec_quantity)
            else:
                profit_quantity = abs(position.quantity)

            if position.direction == DIRECTION.LONG:
                profit = trade.exec_price * profit_quantity - position.open_price * profit_quantity
            else:
                profit = position.open_price * profit_quantity - trade.exec_price * profit_quantity
            self.wallet_balance += profit

        self.wallet_balance -= trade.commission
        position.deal(trade)
