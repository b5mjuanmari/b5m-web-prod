#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime


def c_log(script_path):
    script_name = os.path.splitext(
        os.path.basename(script_path)
    )[0]

    log_folder = os.path.join(
        os.path.dirname(
            os.path.abspath(script_path)
        ),
        "log"
    )

    os.makedirs(
        log_folder,
        exist_ok=True
    )

    log_file = os.path.join(
        log_folder,
        "{}_{}.log".format(
            script_name,
            datetime.now().strftime("%Y%m%d")
        )
    )

    if os.path.exists(log_file):
        os.remove(log_file)

    def log(msg):
        log_line = "{} {}".format(
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            msg
        )

        with open(
            log_file,
            "a",
            encoding="utf-8"
        ) as f:
            f.write(log_line + "\n")

        if sys.stdout.isatty():
            print(log_line)

    return log
