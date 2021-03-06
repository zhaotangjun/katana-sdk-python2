"""
Python 2 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
from __future__ import absolute_import

import logging
import time
import types
import sys

from datetime import datetime

from . import json

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"


class RequestLogger(object):
    """
    Logger for requests.

    It appends the request ID to all logging messages.

    """

    def __init__(self, rid, name):
        self.rid = rid
        self.log = logging.getLogger(name)

    def debug(self, msg, *args, **kw):
        if self.rid:
            self.log.debug(msg + ' |{}|'.format(self.rid), *args, **kw)
        else:
            self.log.debug(msg, *args, **kw)

    def info(self, msg, *args, **kw):
        if self.rid:
            self.log.info(msg + ' |{}|'.format(self.rid), *args, **kw)
        else:
            self.log.info(msg, *args, **kw)

    def warning(self, msg, *args, **kw):
        if self.rid:
            self.log.warning(msg + ' |{}|'.format(self.rid), *args, **kw)
        else:
            self.log.warning(msg, *args, **kw)

    def error(self, msg, *args, **kw):
        if self.rid:
            self.log.error(msg + ' |{}|'.format(self.rid), *args, **kw)
        else:
            self.log.error(msg, *args, **kw)

    def critical(self, msg, *args, **kw):
        if self.rid:
            self.log.critical(msg + ' |{}|'.format(self.rid), *args, **kw)
        else:
            self.log.critical(msg, *args, **kw)

    def exception(self, msg, *args, **kw):
        if self.rid:
            self.log.exception(msg + ' |{}|'.format(self.rid), *args, **kw)
        else:
            self.log.exception(msg, *args, **kw)


class KatanaFormatter(logging.Formatter):
    """Default KATANA logging formatter."""

    def formatTime(self, record, *args, **kwargs):
        utc = time.mktime(time.gmtime(record.created)) + (record.created % 1)
        return datetime.fromtimestamp(utc).isoformat()[:-3]


def value_to_log_string(value, max_chars=100000):
    """Convert a value to a string.

    :param value: A value to log.
    :type value: object
    :param max_chars: Optional maximum number of characters to return.
    :type max_chars: int

    :rtype: str

    """

    if value is None:
        output = 'NULL'
    elif isinstance(value, bool):
        output = 'TRUE' if value else 'FALSE'
    elif isinstance(value, basestring):
        output = value
    elif isinstance(value, (dict, list, tuple)):
        output = json.serialize(value, prettify=True).decode('utf8')
    elif isinstance(value, types.FunctionType):
        if value.__name__ == '<lambda>':
            output = 'anonymous'
        else:
            output = '[function {}]'.format(value.__name__)
    else:
        output = repr(value)

    return output[:max_chars]


def get_output_buffer():
    """Get buffer interface to send logging output.

    :rtype: StringIO

    """

    return sys.stdout


def setup_katana_logging(type, name, version, framework, level=logging.INFO):
    """Initialize logging defaults for KATANA.

    :param type: Component type.
    :param name: Component name.
    :param version: Component version.
    :param framework: KATANA framework version.
    :param level: Logging level. Default: INFO.

    """

    format = "%(asctime)sZ {} [%(levelname)s] [SDK] %(message)s".format(
        "{} {}/{} ({})".format(type, name, version, framework)
        )

    output = get_output_buffer()

    # Setup root logger
    root = logging.root
    if not root.handlers:
        logging.basicConfig(level=level, stream=output)
        root.setLevel(level)
        root.handlers[0].setFormatter(KatanaFormatter(format))

    # Setup katana logger
    logger = logging.getLogger('katana')
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler(stream=output)
        handler.setFormatter(KatanaFormatter(format))
        logger.addHandler(handler)
        logger.propagate = False

    # Setup katana api logger
    logger = logging.getLogger('katana.api')
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        handler = logging.StreamHandler(stream=output)
        handler.setFormatter(KatanaFormatter(format))
        logger.addHandler(handler)
        logger.propagate = False
