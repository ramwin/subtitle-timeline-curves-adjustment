#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import bisect
import datetime
import json

import ass
import click

from curve_adjustment import modify


def get_seconds(time_str: str):
    """
    00:10:12 -> 612
    """
    hour, minute, second = map(int, time_str.split(":"))
    return hour * 3600 + minute * 60 + second


def get_anchor(start_times, anchors):
    """
    given start time of multi subtitles, and the target time of anchors. return the anchor config

    start_times: [
        33.33, 54.87, 60.82, 
    ]
    anchors: {
        '00:00:54': '00:00:58',
    }
    return {
        1: 4  # this index=1 subtitle should add 4 seconds
    }
    """
    result = {}
    for subtitle_time_str, video_time_str in anchors.items():
        subtitle_time = get_seconds(subtitle_time_str)
        target_time = get_seconds(video_time_str)
        delta = target_time - subtitle_time

        index = bisect.bisect(start_times, subtitle_time)
        result[index] = delta
    return result


@click.option("--source", help="input ass path")
@click.option("--target", help="output ass path", default="output.ass")
@click.option("--config", help="anchors json path")
def main(source, target, anchorconfig):
    """
    convert a ass file with anchor config
    anchor config:

        what the real time of as ass dialog time

        {
            "01:10:30": "01:11:30",
        }

    """
    with open(source) as source_file:
        sections = ass.parse(source_file)

    subtitle_start_seconds = [
        dialog.start.total_seconds()
        for dialog in sections.events
    ]
    subtitle_end_seconds = [
        dialog.end.total_seconds()
        for dialog in sections.events
    ]

    with open(anchorconfig) as anchor_file:
        anchors = json.load(anchor_file)
        if "anchors" in anchors:
            anchors = anchors["anchors"]

    start_anchor = get_anchor(
        subtitle_start_seconds, anchors
    )
    end_anchor = get_anchor(
        subtitle_end_seconds, anchors
    )

    for index, (start_second, end_second) in enumerate(zip(
        modify(subtitle_start_seconds, start_anchor),
        modify(subtitle_end_seconds, end_anchor),
    )):
        sections.events[index].start = datetime.timedelta(start_second)
        sections.events[index].end = datetime.timedelta(end_second)

    with open(target, 'w') as target_file:
        sections.dump_file(target_file)
