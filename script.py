#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import bisect
import datetime
import json
import logging
from pathlib import Path

import ass
import click
import pysrt

from curve_adjustment import modify


logging.basicConfig(
    level=logging.DEBUG,
    handlers=[logging.StreamHandler()],
    format="%(asctime)s %(pathname)s[line:%(lineno)d] %(levelname)s %(message)s",
)
LOGGER = logging.getLogger(__name__)
logging.getLogger("curve_adjustment").setLevel(logging.INFO)


def get_seconds(time_str: str) -> float:
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


def get_sub_seconds(sub_time) -> float:
    return sub_time.hours * 3600 + sub_time.minutes * 60 + sub_time.seconds + sub_time.milliseconds / 1000


@click.command()
@click.option("--source", help="input ass path")
@click.option("--target", help="output ass path", default="output.ass")
@click.option("--config", help="anchors json path", default="config.json")
def main(source, target, config):
    """
    convert a ass file with anchor config
    anchor config:

        what the real time of as ass dialog time

        {
            "01:10:30": "01:11:30",
        }

    """
    source = Path(source)
    with open(config) as anchor_file:
        anchors = json.load(anchor_file)
        if "anchors" in anchors:
            anchors = anchors["anchors"]

    if source.suffix.lower() == ".ass":

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

    elif source.suffix.lower() == ".srt":

        subs = pysrt.open(source, encoding="utf8")

        subtitle_start_seconds = [
            get_sub_seconds(sub.start)
            for sub in subs
        ]
        subtitle_end_seconds = [
            get_sub_seconds(sub.end)
            for sub in subs
        ]

    start_anchor = get_anchor(
        subtitle_start_seconds, anchors
    )
    end_anchor = get_anchor(
        subtitle_end_seconds, anchors
    )
    LOGGER.info("start_anchor: %s", start_anchor)
    LOGGER.info("end_anchor: %s", end_anchor)



    if source.suffix.lower() == ".ass":
        start_mod = modify(subtitle_start_seconds, start_anchor)
        end_mod = modify(subtitle_end_seconds, end_anchor)
        LOGGER.info("start_mod: %s", start_mod)
        for index, (start_second, end_second) in enumerate(zip(
            start_mod, end_mod
        )):
            sections.events[index].start = datetime.timedelta(seconds=start_second)
            sections.events[index].end = datetime.timedelta(seconds=end_second)

        with open(target, 'w') as target_file:
            sections.dump_file(target_file)

    elif source.suffix.lower() == ".srt":
        start_mod = modify(subtitle_start_seconds, start_anchor,
                           output_format="delta")
        end_mod = modify(subtitle_end_seconds, end_anchor,
                         output_format="delta")
        LOGGER.info("start_mod: %s", start_mod)
        for index, start_delta in enumerate(start_mod):
            subs[index].shift(seconds=start_delta)

        subs.save(target)


if __name__ == "__main__":
    main()
