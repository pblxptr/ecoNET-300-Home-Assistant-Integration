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

## Boiler staus keys map
# boiler mode names from  endpoint http://LocalIP/econet/rmParamsEnums?
OPERATION_MODE_NAMES = {
    0: "TURNED OFF",
    1: "FIRE UP",
    2: "STABILIZATION",
    3: "WORK",
    4: "SUPERVISION",
    5: "Halted",
    6: "STOP",
    7: "BURNING OFF",
    8: "MANUAL",
    9: "ALARM",
    10: "UNSEALING",
    11: "CHIMNEY",
    12: "ACTIVACTION",
    13: "NO TRANSMISSION",
}
