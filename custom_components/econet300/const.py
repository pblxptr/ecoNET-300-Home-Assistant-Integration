"""Constants for the econet Integration integration."""

DOMAIN = "econet300"

SERVICE_API = "api"
SERVICE_COORDINATOR = "coordinator"

DEVICE_INFO_MANUFACTURER = "PLUM"
DEVICE_INFO_MODEL = "ecoNET300"
DEVICE_INFO_NAME = "PLUM ecoNET300"

CONF_ENTRY_TITLE = "ecoNET300"
CONF_ENTRY_DESCRIPTION = "PLUM Econet300"

## Sys params
API_SYS_PARAMS_URI = "sysParams"
API_SYS_PARAMS_PARAM_UID = "uid"

## Reg params
API_REG_PARAMS_URI = "regParams"
API_REG_PARAMS_PARAM_DATA = "curr"

## Editable params limits
API_EDIT_PARAM_URI = "rmCurrNewParam"
API_EDITABLE_PARAMS_LIMITS_URI = "rmCurrentDataParamsEdits"
API_EDITABLE_PARAMS_LIMITS_DATA = "data"

## Params mapping
EDITABLE_PARAMS_MAPPING_TABLE = {
    "tempCOSet": '1280',
    "tempCWUSet": '1281',
    "mixerSetTemp1": '1287',
    "mixerSetTemp2": '1288',
    "mixerSetTemp3": '1289',
    "mixerSetTemp4": '1290',
    "mixerSetTemp5": '1291',
    "mixerSetTemp6": '1292',
}
