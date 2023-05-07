#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import logging
import unittest

from curve_adjustment import modify


stream_handler = logging.StreamHandler()

logging.captureWarnings(True)
logging.basicConfig(
    level=logging.DEBUG,
    format=(
        '%(asctime)s %(pathname)s[line:%(lineno)d] %(levelname)s %(message)s'
    ),
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        stream_handler,
    ],
)
LOGGER = logging.getLogger(__name__)


class Test(unittest.TestCase):

    def test1(self):
        origin = [1, 4, 7, 9, 11]
        anchors = {
            2: -2
        }
        target = [1, 3, 5, 8, 11]
        results = modify(origin, anchors)
        LOGGER.debug("results: %s", results)
        assert results == target

    def test2(self):
        origin = [1, 2, 3, 9, 9.5, 10]
        anchors = {
            2: 3
        }
        target = [1, 3.5, 6,
                  9.428571428571429,
                  9.714285714285715,
                  10]
        results = modify(origin, anchors)
        LOGGER.debug("results: %s", results)
        assert results == target
