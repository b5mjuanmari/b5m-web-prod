#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime


def sortu_logger(script_path):

    script_izena = os.path.splitext(
        os.path.basename(script_path)
    )[0]

    log_karpeta = os.path.join(
        os.path.dirname(
            os.path.abspath(script_path)
        ),
        "log"
    )

    os.makedirs(
        log_karpeta,
        exist_ok=True
    )

    log_fitxategia = os.path.join(
        log_karpeta,
        "{}_{}.log".format(
            script_izena,
            datetime.now().strftime("%Y%m%d")
        )
    )

    if os.path.exists(log_fitxategia):
        os.remove(log_fitxategia)

    def log(mezua):

        lerroa = "{} {}".format(
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            mezua
        )

        with open(
            log_fitxategia,
            "a",
            encoding="utf-8"
        ) as f:
            f.write(lerroa + "\n")

        if sys.stdout.isatty():
            print(lerroa)

    return log
