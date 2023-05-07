#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


"""
apply linear change to a data sequence
"""

import logging


LOGGER = logging.getLogger(__name__)


def modify(origin: list, anchors: dict, output_format="value") -> list:
    """
    Given a sorted data list and some modify in specifix position,
    this function will apply the modify linearly.

    :params output_format: default value, return target value, return delta if output_format is 'delta'
    Examples:

           y
           │                              *     10
           │                          *  9.5
           │                          9
           │
           │      *(move the 3 upper)
           │
           │   *(this will also get higher linearly)
           │
           │      3
           │   2
           │ 1
           └-------------------------------------------------> x

        origin: [1, 2, 3,                    9, 9.5, 10]

        anchors: {
            2: 3
        }
        return: [1, 3.5, 6,                 9.4 9.7, 10.0]
    realization:

        1. get the modification for each anchor (and head tail set default 0 if not specificated)
            mod:     [0, null, +3, null, null, 0]

        2. get the linear change

            factor between [1, 2, 3] = +3 / (3-1) = 1.5
            factor between [3, 9, 9.5, 10] = +3 / (10-3) = 0.42847
            mod:     [0, +1.5, +3, +2,   +1,   0]

        3. apply the linear change
            results: [1, 3.5, 6,
                      9 + (7 - (9-3)) * 0.42847 = 9.4
                      9.5 + (7 - (9.5-3)) * 0.42847 = 9.7,
                      10 + (7 - (10-3)) * 0.42847 = 10.0,
                     ]
    """

    mod = [None] * len(origin)
    mod[0] = 0
    mod[-1] = 0

    for key, value in anchors.items():
        mod[key] = value

    # anchor_indexes = [0, 2, 5] for example
    anchor_indexes = sorted(
        set(anchors.keys()).union({0, len(mod) - 1})
    )
    LOGGER.debug("anchor_indexes = %s", anchor_indexes)
    LOGGER.debug("before linear mod = %s", mod)
    for i in range(len(anchor_indexes) - 1):
        start_index = anchor_indexes[i]
        end_index = anchor_indexes[i+1]
        start_delta = mod[start_index]
        end_delta = mod[end_index]
        factor = (end_delta - start_delta) / (
            origin[end_index] - origin[start_index]
        )
        for i in range(start_index + 1, end_index):
            mod[i] = mod[start_index] + factor * (origin[i] - origin[start_index])

    LOGGER.debug("mod = %s", mod)

    if output_format == 'delta':
        return mod
    return [
        value + mod[i]
        for i, value in enumerate(origin)
    ]
