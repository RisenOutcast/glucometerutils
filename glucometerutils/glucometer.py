#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-FileCopyrightText: © 2013 The glucometerutils Authors
# SPDX-FileCopyrightText: © 2025 RisenOutcast
# SPDX-License-Identifier: MIT
# Utility to manage glucometers' data.

import argparse
import logging
from pathlib import Path
from config import FOLDERS

def main():
    def get_logs_dir():
        my_documents = Path.home() / "Documents"

        folder_path = my_documents.joinpath(*FOLDERS)
        logs_dir = folder_path / "Logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir

    def configure_logging():
        logs_dir = get_logs_dir()
        log_path = logs_dir / "glucometer_log.txt"

        logging.basicConfig(
            filename=str(log_path),
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
        )

    configure_logging()
    
    try:
        from glucometerutils import common, driver, exceptions
    except Exception:
        logging.exception("Failed to import glucometerutils submodules")
        return 1

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action")

    parser.add_argument(
        "--driver",
        action="store",
        required=True,
        help="Select the driver to use for connecting to the glucometer.",
    )

    parser.add_argument(
        "--device",
        action="store",
        required=False,
        help=(
            "Select the path to the glucometer device. Some devices require "
            "this argument, others will try autodetection."
        ),
    )

    subparsers.add_parser("info", help="Display information about the meter.")

    subparsers.add_parser(
        "dump", help="Dump the readings stored in the device."
    )

    args = parser.parse_args()

    try:
        requested_driver = driver.load_driver(args.driver)
    except ImportError as e:
        logging.error(
            'Error importing driver "%s", please check your --driver parameter:\n%s',
            args.driver,
            e,
        )
        return 1
    
    try:
        device = requested_driver.device(args.device)

        device.connect()
        device_info = device.get_meter_info()
    except exceptions.Any as err:
        logging.error(f"Error while executing '{args.action}': {err}")

    try:
        if args.action == "info":
            logging.info("Info called.")
            try:
                time_str = device.get_datetime()
            except exceptions.InvalidDateTime:
                time_str = "INVALID"
            # Also catch any leftover ValueErrors.
            except (NotImplementedError, ValueError):
                time_str = "N/A"
            print(f"{device_info},{time_str}")
            logging.info("Info: " + f"{device_info},{time_str}")
        elif args.action == "dump":
            logging.info("Dump called.")
            unit = device_info.native_unit

            readings = device.get_readings()
            readings_count = 0

            readings = (
                reading
                for reading in readings
                if not isinstance(reading, common.KetoneReading)
            )

            for reading in sorted(readings, key=lambda r: r.timestamp):
                readings_count +=1
                
            logging.info("Dumped %d readings from device.", readings_count)
        else:
            return 1
    except exceptions.Error as err:
        logging.error(f"Error while executing '{args.action}': {err}")
        return 1

    device.disconnect()
    return 0
