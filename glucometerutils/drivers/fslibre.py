# -*- coding: utf-8 -*-
#
# SPDX-FileCopyrightText: © 2017 The glucometerutils Authors
# SPDX-License-Identifier: MIT
# Driver for FreeStyle Libre devices.

# Supported features:
#    - get readings (sensor, flash and blood glucose), including comments;
#    - get and set date and time;
#    - get serial number and software version;
#    - get and set patient name;
#    - memory reset (caution!)

# Expected device path: /dev/hidraw9 or similar HID device. Optional when using HIDAPI.

# Further information on the device protocol can be found at
# https://protocols.glucometers.tech/abbott/freestyle-libre


from typing import Optional

from glucometerutils.support import freestyle_libre


class Device(freestyle_libre.LibreDevice):
    _MODEL_NAME = "FreeStyle Libre"

    def __init__(self, device_path: Optional[str]) -> None:
        super().__init__(0x3650, device_path, encoding="utf-8")
