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

from MonkTrader.utils import assure_dir, CsvFileDefaultDict
import csv
import pytest
import tempfile
import os

def test_assure_home():
    tmp_dir = tempfile.gettempdir()
    assert assure_dir(tmp_dir)

    with tempfile.NamedTemporaryFile() as f:
        with pytest.raises(NotADirectoryError):
            assure_dir(f.name)

def test_csv_file_defaultdict():
    with tempfile.TemporaryDirectory() as tdir:
        headers = ['1','2', '3']
        csv_d = CsvFileDefaultDict(tdir, headers)

        f1 = csv_d['123']
        assert isinstance(f1, csv.DictWriter)

        f1.writerow({'1':'3', '2':'2', '3':'1'})

        csv_d.close()

        assert os.path.isfile(os.path.join(tdir, '123.csv'))

        with open(os.path.join(tdir, '123.csv'), 'r') as f:
            content = f.read()

        assert content == "1,2,3{}3,2,1{}".format(CsvFileDefaultDict.CSVNEWLINE, CsvFileDefaultDict.CSVNEWLINE)