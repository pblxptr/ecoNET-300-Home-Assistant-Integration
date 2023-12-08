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

ALARMS_NAMES = {
    0: "No power",
    1: "Boiler sensor error",
    2: "Exceeding the maximum temperature of the boiler",
    3: "Sensor fault feeder",
    4: "Exceeding the maximum temperature of the tray",
    5: "Sensor fault system",
    6: "Exceeding the maximum flue gas temperature",
    7: "Firing up the boiler failed",
    8: "No fuel",
    9: "Loss of Containment",
    10: "Pressure sensor failed",
    11: "Faulty fan ",
    12: "ID Fan Pressure can not be reached ",
    13: "Burning off error ",
    14: "Photocell sensor failed",
    15: "Linear actuator blocked",
    16: "Incorrect work parameters",
    17: "Precaution of condensation ",
    18: "STB is disabled . Manual reset is needed when TB <65 °C Boiler STB ",
    19: "Opening the contact STB tray ",
    20: "Minimum water pressure exceeded",
    21: "Maximum water pressure exceeded",
    22: "Fuel feeder locked",
    23: "Extinguished flame ",
    24: "Faulty exhaust fan",
    25: "Error loading external feeder ",
    26: "Error Sensor solar collector SH ",
    27: "Error Sensor solar circuit SL ",
    28: "Sensor fault circuit H1- S",
    29: "Sensor fault circuit H2 - S",
    30: "Sensor fault circuit H3 - S",
    31: "Error weather sensor WS ",
    32: "HUW sensor error ",
    33: "Sensor error H0- S",
    34: "It takes frost protection - heat source are not included ",
    35: "It takes frost protection - the source of the attached ",
    36: "Exceeded max. Temperature solar collector ",
    37: "Exceeded max. Flow temperature of the floor ",
    38: "Cooling preventive solid fuel boiler ",
    39: "No communication with ecoLAMBDA ",
    40: "Lock the primary air damper ",
    41: "Lock the secondary air damper ",
    42: "Feeder full",
    43: "Furnace full",
    44: "No communication with B module",
    45: "Cleaning servomotor error",
    46: "Minimum pressure exceeded",
    47: "Maximum pressure exceeded",
    48: "Pressure sensor damage",
    49: "Maximum main heat source temperature exceeded",
    50: "Maximum additional heat source temperature exceeded",
    51: "Solar is OFF - temperature  is too high - wait for temperature drop",
    52: "Alarm for auger control system malfunction",
    53: "Clogged auger Alarm",
    54: "Temperature above maximum for the thermocouple.",
    55: "Thermocouple wired improperly.",
    255: "Alarm unknown"
}
