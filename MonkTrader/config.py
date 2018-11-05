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

from traitlets.config import Configurable
from traitlets import Unicode, observe, Bool
import os
import sys
import importlib
import pymongo
from MonkTrader import _settings

def import_path(fullpath):
    """
    Import a file with full path specification. Allows one to
    import from anywhere, something __import__ does not do.
    """
    path, filename = os.path.split(fullpath)
    filename, ext = os.path.splitext(filename)
    sys.path.insert(0, path)
    module = importlib.import_module(filename, path)
    importlib.reload(module)  # Might be out of date
    del sys.path[0]
    return module

# for k, attr in base_settings.keys
base_settings = {}
for k,attr in vars(_settings).items():
    if k.startswith("__"):
        continue
    base_settings.update({k:attr})


class Config(Configurable):

    DATABASE_URI =Unicode(config=True, default_value="mongodb://127.0.0.1:27017")

    IS_TEST = Bool(config=True)

    API_KEY = Unicode(config=True)
    API_SECRET = Unicode(config=True)


    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)

        self._db_handle = pymongo.MongoClient(self.DATABASE_URI)

    @observe('DATABASE_URI')
    def _observe_database_uri(self, change):
        new = change.get('new')
        self._db_handle = pymongo.MongoClient(new)

    @property
    def db(self):
        return self._db_handle


config = Config(**base_settings)