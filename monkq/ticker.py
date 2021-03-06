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
from typing import Generator

from dateutil.rrule import DAILY, MINUTELY, rrule
from monkq.exception import SettingError
from monkq.utils.i18n import _
from monkq.utils.timefunc import is_aware_datetime

FREQ_DICT = {'1m': MINUTELY, '1d': DAILY}


class FrequencyTicker():
    def __init__(self, start_time: datetime.datetime, end_time: datetime.datetime, frequency: str):
        assert is_aware_datetime(start_time)
        assert is_aware_datetime(end_time)

        if start_time >= end_time:
            raise SettingError(_("START TIME can not bigger than END TIME"))
        self.start_time = start_time
        self.end_time = end_time
        self.frequency = FREQ_DICT.get(frequency)

        self.current = start_time

    def timer(self) -> Generator[datetime.datetime, None, None]:
        for current_datetime in rrule(self.frequency, dtstart=self.start_time, until=self.end_time):
            self.current = current_datetime
            yield self.current
