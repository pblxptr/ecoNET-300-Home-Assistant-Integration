"""Constants for the econet Integration integration."""

DOMAIN = "econet300"

SERVICE_API = "api"
SERVICE_COORDINATOR = "coordinator"

DEVICE_INFO_MANUFACTURER = "PLUM"
DEVICE_INFO_MODEL = "ecoNET300"
DEVICE_INFO_CONTROLLER_NAME = "PLUM ecoNET300"
DEVICE_INFO_MIXER_NAME = "Mixer"

CONF_ENTRY_TITLE = "ecoNET300"
CONF_ENTRY_DESCRIPTION = "PLUM Econet300"

## Sys params
API_SYS_PARAMS_URI = "sysParams"
API_SYS_PARAMS_PARAM_UID = "uid"
API_SYS_PARAMS_PARAM_SW_REV = "softVer"
API_SYS_PARAMS_PARAM_HW_VER = "routerType"

## Reg params
API_REG_PARAMS_URI = "regParams"
API_REG_PARAMS_PARAM_DATA = "curr"

## Editable params limits
API_EDIT_PARAM_URI = "rmCurrNewParam"
API_EDITABLE_PARAMS_LIMITS_URI = "rmCurrentDataParamsEdits"
API_EDITABLE_PARAMS_LIMITS_DATA = "data"

## Params mapping
EDITABLE_PARAMS_MAPPING_TABLE = {
    "tempCOSet": "1280",
    "tempCWUSet": "1281",
    "mixerSetTemp1": "1287",
    "mixerSetTemp2": "1288",
    "mixerSetTemp3": "1289",
    "mixerSetTemp4": "1290",
    "mixerSetTemp5": "1291",
    "mixerSetTemp6": "1292",
}

AVAILABLE_NUMBER_OF_MIXERS = 6

## Boiler staus keys map
# boiler mode names from  endpoint http://LocalIP/econet/rmParamsEnums?
OPERATION_MODE_NAMES = {
    0: "TURNED OFF",
    1: "FIRE UP",
    2: "FIRE UP",
    3: "WORK",
    4: "SUPERVISION",
    5: "Halted",
    6: "STOP",
    7: "BURNING OFF",
    8: "MANUAL",
    9: "ALARM",
    10: "UNSEALING",
    11: "CHIMNEY",
    12: "STABILIZATION",
    13: "NO TRANSMISSION",
}

# add constants to future
PRODUCT_TYPE = {
    0: "ECOMAX_850P_TYPE",  # regType 0
    1: "ECOMAX_850i_TYPE",  # regType 1
}

# Sensors precision value from econet dev
REG_PARAM_PRECICION = {
    "boilerPowerKW": 1,
    "boilerPower": 0,
    "fuelStream": 1,
    "ecoSterTemp": 1,
    "ecoSterSetTemp": 1,
    "tempExternalSensor": 1,
    "lambdaSet": 1,
    "lambdaLevel": 1,
    "thermoTemp": 1,
    "thermoSetTemp": 0,
    "tempFeeder": 0,
    "tempCO": 0,
    "tempFlueGas": 0,
    "tempCWU": 0,
    "tempCWUSet": 0,
    "tempUpperBuffer": 0,
}
