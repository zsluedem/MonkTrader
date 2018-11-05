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

import shutil
import click
import os
from MonkTrader.logger import console_log
from MonkTrader.config import config
from MonkTrader.data import save_kline, save_symbols

@click.group()
def cli():
    pass


@click.command()
@click.help_option()
@click.option('--mongodb_uri', default='mongodb://127.0.0.1:27017', help="mongodb uri you want to download to")
@click.option('--active', default=True, type=click.BOOL ,help="download active or all symbols")
@click.option('--frequency', default="all", type=click.Choice(['all', '1m', '5m', '1h', '1d']))
def download(mongodb_uri, active, frequency):
    config.database_uri = mongodb_uri
    save_symbols(active)

    if frequency == "all":
        save_kline('1m', active)
        save_kline('5m', active)
        save_kline('1h', active)
        save_kline('1d', active)
    else:
        save_kline(frequency, active)


@click.command()
def run():
    pass

@click.command()
@click.help_option()
@click.option("--target_dir", default=".", help="The target dir where would generate a default setting file")
def generate_settings(target_dir):
    package_base = os.path.dirname(__file__)

    target_dir = os.path.realpath(target_dir)
    if not os.path.isdir(target_dir):
        console_log.error("Please provide a valid target dir!!!")
        return

    shutil.copy(os.path.join(package_base, "_settings.py"), os.path.join(target_dir, "setting.py"))

    console_log.info("Successfully generated the setting file, please edit your setting.")

cli.add_command(download)
cli.add_command(run)
cli.add_command(generate_settings)

def cmdEntry():
    cli()


if __name__ == '__main__':
    cli()