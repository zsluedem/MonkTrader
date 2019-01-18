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
from abc import ABC, abstractmethod, abstractproperty
from typing import TypeVar, TYPE_CHECKING, List

if TYPE_CHECKING:
    from MonkTrader.assets.instrument import Instrument
    from MonkTrader.assets.order import BaseOrder

T_INSTRUMENT = TypeVar('T_INSTRUMENT', bound="Instrument")
T_ORDER = TypeVar("T_ORDER", bound="BaseOrder")


class AbcInstrument(ABC):
    pass


class AbcAccount(ABC):
    pass


class AbcPosition(ABC):
    pass


class AbcPositions(ABC):
    @abstractmethod
    def get(self, instrument: AbcInstrument) -> AbcPosition:
        raise NotImplementedError()


class AbcOrder(ABC):
    pass


class AbcTrade(ABC):
    pass


class AbcExchange(ABC):
    @abstractmethod
    def get_last_price(self, instrument: T_INSTRUMENT) -> float:
        raise NotImplementedError()

    @abstractmethod
    def withdraw(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def deposit(self) -> None:
        raise NotImplementedError()

    @abstractproperty
    def exchange_info(self) -> None:
        raise NotImplementedError()

    @abstractproperty
    def order_book(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_account(self) -> AbcAccount:
        raise NotImplementedError()

    @abstractmethod
    def place_limit_order(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def place_market_order(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def place_stop_limit_order(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def place_stop_market_order(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def open_orders(self) -> List[T_ORDER]:
        raise NotImplementedError()

    @abstractmethod
    def cancel_order(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def available_instruments(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def setup(self) -> None:
        raise NotImplementedError()
