# -*- coding: utf-8 -*-
#
# SPDX-FileCopyrightText: © 2013 The glucometerutils Authors
# SPDX-FileCopyrightText: © 2025 RisenOutcast
# SPDX-License-Identifier: MIT
# Common routines for data in glucometers.

from dataclasses import dataclass, field
import datetime
import enum
import logging
import os
from typing import Any, Optional, Union, Sequence

class Unit(enum.Enum):
    MG_DL = "mg/dL"
    MMOL_L = "mmol/L"

# Constants for meal information
class Meal(enum.Enum):
    NONE = ""
    BEFORE = "Before Meal"
    AFTER = "After Meal"

# Constants for measure method
class MeasurementMethod(enum.Enum):
    BLOOD_SAMPLE = "blood sample"
    CGM = "CGM"  # Continuous Glucose Monitoring
    TIME = "time"

def convert_glucose_unit(value: float, from_unit: Unit, to_unit: Unit) -> float:
    # Convert the given value of glucose level between units.

    # Args:
    #   value: The value of glucose in the current unit
    #   from_unit: The unit value is currently expressed in
    #   to_unit: The unit to conver the value to: the other if empty.
 
    # Returns:
    #   The converted representation of the blood glucose level.

    from_unit = Unit(from_unit)
    to_unit = Unit(to_unit)

    if from_unit == to_unit:
        return value

    if from_unit == Unit.MG_DL:
        return round(value / 18.0, 2)

    return round(value * 18.0, 1)

@dataclass
class GlucoseReading:
    timestamp: datetime.datetime
    value: float
    meal: Meal = Meal.NONE
    comment: str = ""
    measure_method: MeasurementMethod = MeasurementMethod.BLOOD_SAMPLE
    extra_data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.meal, Meal):
            self.meal = Meal(self.meal)
        if not isinstance(self.measure_method, MeasurementMethod):
            self.measure_method = MeasurementMethod(self.measure_method)

    def get_value_as(self, to_unit: Unit) -> float:
        # Returns the reading value as the given unit.
 
        # Args:
        #   to_unit: The unit to return the value to.

        return convert_glucose_unit(self.value, Unit.MG_DL, to_unit)

    def as_csv(self, unit: Unit) -> str:
        # Returns the reading as a formatted comma-separated value string.
        return '%s,%.2f,%s,%s,%s' % (
            self.timestamp,
            self.get_value_as(unit),
            self.meal.value,
            self.measure_method.value,
            self.comment,
        )
    
    def save_to_file(self, List: list) -> str:
        file_name = 'readings.csv'
        full_path = os.path.abspath(file_name)
        
        with open(full_path, 'w') as f:
            for line in List:
                f.write(f"{line}\n")
                
        logging.info(f"File successfully saved to: {full_path}")

@dataclass
class KetoneReading:
    timestamp: datetime.datetime
    value: float
    comment: str = ""
    measure_method: MeasurementMethod = MeasurementMethod.BLOOD_SAMPLE
    extra_data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.measure_method is not MeasurementMethod.BLOOD_SAMPLE:
            raise ValueError("KetoneReading.measure_method must be BLOOD_SAMPLE")

    def as_csv(self, unit: Unit) -> str:
        # Returns the reading as a formatted comma-separated value string.
        del unit  # Unused for Ketone readings.

        return '"%s","%.2f","","%s","%s"' % (
            self.timestamp,
            self.value,
            self.measure_method.value,
            self.comment,
        )

@dataclass
class TimeAdjustment:
    timestamp: datetime.datetime
    old_timestamp: datetime.datetime
    measure_method: MeasurementMethod = MeasurementMethod.TIME
    extra_data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.measure_method, MeasurementMethod):
            self.measure_method = MeasurementMethod(self.measure_method)

    def as_csv(self, unit: Unit) -> str:
        del unit
        return '"%s","","","%s","%s"' % (
            self.timestamp,
            self.measure_method.value,
            self.old_timestamp,
        )

AnyReading = Union[GlucoseReading, KetoneReading, TimeAdjustment]

@dataclass
class MeterInfo:
    # General information about the meter.
 
    # Attributes:
    #   model: Human readable model name, chosen by the driver.
    #   serial_number: Serial number identified for the reader (or N/A if not available in the protocol.)
    #   version_info: List of strings with any version information available about the device. It can include hardware and software version.
    #   native_unit: One of the Unit values to identify the meter native unit.

    model: str
    serial_number: str = "N/A"
    version_info: Sequence[str] = ()
    native_unit: Unit = Unit.MG_DL
    patient_name: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.native_unit, Unit):
            self.native_unit = Unit(self.native_unit)

    def __str__(self) -> str:
        version_information_string = "N/A"
        if self.version_info:
            version_information_string = "\n                ".join(self.version_info).strip()
        return f"{self.model},{self.serial_number},{version_information_string},{self.native_unit.value},{self.patient_name}"
