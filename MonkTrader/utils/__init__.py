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
import csv
import os
from collections import defaultdict
from typing import List, Any, Set, Type, IO
import datetime
import gzip


def assure_dir(dir: str) -> bool:
    """
    Assure dir is a directory.
    :param dir:
    :return: If dir is a directory , return True, else create the directory and return False
    :raise NotADirectoryError: if param dir is a file , raise NotADirectoryError
    """
    if os.path.isdir(dir):
        return True
    else:
        try:
            os.mkdir(dir)
        except FileExistsError:
            raise NotADirectoryError()
        return False


def is_aware_datetime(t: datetime.datetime) -> bool:
    return t.tzinfo is not None and t.tzinfo.utcoffset(t) is not None


class CsvFileDefaultDict(defaultdict):
    CSVNEWLINE = '\n'  # type: str

    def __init__(self, dir: str, fieldnames: List[str], *args: Any, **kwargs: Any) -> None:
        super(CsvFileDefaultDict, self).__init__(*args, **kwargs)
        self.dir = dir
        self.default_factory = csv.DictWriter  # type: Type[csv.DictWriter]
        self.fieldnames = fieldnames
        self.file_set = set()  # type: Set

    def __missing__(self, key: str) -> csv.DictWriter:
        f = open(os.path.join(self.dir, '{}.csv'.format(key)), 'w', newline=self.CSVNEWLINE)
        self.file_set.add(f)
        ret = self[key] = self.default_factory(f, fieldnames=self.fieldnames)
        ret.writeheader()
        return ret

    def close(self):
        for f in self.file_set:
            f.close()


class CsvZipDefaultDict(defaultdict):
    CSVNEWLINE = '\n'  # type: str

    def __init__(self, dir: str, fieldnames: List[str], level: int = -1, *args, **kwargs):
        super(CsvZipDefaultDict, self).__init__(*args, **kwargs)
        self.dir = dir
        self.fieldnames = fieldnames
        self._level = level
        self.default_factory = gzip.open

        self.file_set = set()  # type: Set[IO]

    def __missing__(self, key):
        f = gzip.open(os.path.join(self.dir, '{}.csv.gz'.format(key)), 'wb')
        self.writerow(f, self.fieldnames)
        self.file_set.add(f)
        ret = self[key] = f
        return ret

    def writerow(self, f: IO, row: List):
        data = ','.join(row)
        data += self.CSVNEWLINE
        data = data.encode('utf8')
        f.write(data)

    def close(self):
        for f in self.file_set:
            f.close()
