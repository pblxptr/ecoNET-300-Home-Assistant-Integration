from dataclasses import dataclass

from homeassistant.helpers.entity import DeviceInfo


class EconetDeviceInfo(DeviceInfo):
    """EconetDeviceInfo"""
    uid: str
