import os

from MonkTrader.const import RUN_TYPE

# Mongodb uri which is used to load data or download data in.
DATABASE_URI = "mongodb://127.0.0.1:27017"

# HTTP Proxy
HTTP_PROXY = ""

# used only for testing
SSL_PATH = ''

FREQUENCY = 'tick'  # tick, 1m ,5m ,1h

LOG_LEVEL = 'INFO'  # DEBUG, INFO, NOTICE, WARNING, ERROR

START_TIME = '2018-01-01T00:00:00Z'
END_TIME = '2018-06-01T00:00:00Z'

RUN_TYPE = RUN_TYPE.BACKTEST  # type: ignore

TICK_TYPE = 'tick'  # tick , bar

STRATEGY = "strategy.MyStrategy"

DATA_DIR = os.path.expanduser("~/.monk/data")

EXCHANGES = {  # type: ignore
    'bitmex': {
        'engine': 'MonkTrader.exchange.bitmex',
        "IS_TEST": True,
        "API_KEY": '',
        "API_SECRET": ''
    }
}

BUILTIN_PLUGINS = {  # type: ignore

}

INSTALLED_PLUGINS = {  # type: ignore

}
