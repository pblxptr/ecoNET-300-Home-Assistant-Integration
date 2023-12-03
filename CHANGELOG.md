## v0.1.0

### Added (6)
* [Entity/Sensor] Added `feeder temperature`
* [Entity/Sensor] Added `fan power`
* [Entity/Sensor] Added `exhaust emperature`
* [Entity/Sensor] Added `fireplace temperature`
* [Entity/Sensor] Added `water back temperature`
* [Entity/Sensor] Added `water temperature`
* [Entity/Sensor] Added `outside temperature`
* [Entity/Sensor] Added `boiler power output`
* [Entity/BinarySensor] Added `water pump works`
* [Entity/BinarySensor] Added `fireplace pump works`
* [Entity/BinarySensor] Added `solar pump works`
* [Entity/BinarySensor] Added `lighter works`
* [Config] Added config via GUI

## v0.1.1
Add new sensors and binary sensor
Add hardware version

## v0.1.5
[Entity/Sensor] Added `lambdaLevel`
[Entity/Sensor] Added `Wi-Fi signal strength`
[Entity/Sensor] Added `Wi-Fi signal quality`
[Entity/Sensor] Added `Module ecoNET software version`
[Entity/Sensor] Added `Module A version`
[Entity/Sensor] Added `Module B version`
[Entity/Sensor] Added `Module Panel version`
[Entity/Sensor] Added `Module Lambda version`

## v0.1.6
fix error in Entity sensor.wi_fi_signal_quality

## v0.1.7
Added `Thermostat sensor` ON or OFF
Added `lambdaStatus`
Added `mode` boiler operation names to status

## v0.1.7-3
Rename boiler mode names
Added `protocol_Type` to DIAGNOSTIC sensor
Added `controllerID` to DIAGNOSTIC sensor   

## v0.1.8
Added REG_PARAM_PRECICION parameters from econet dev file
Added translations for the sensors
Added translations dictonary
By default sensors off: Fan2, Solar pump, Fireplace pump
Changed depricated unit TEMP_CELSIUS to UnitOfTemperature.CELSIUS

## [v0.3.0] 2023-11-30
Thank for @pblxptr add new code line from him
- Added: [New features boiler set temperature]
- Added: [Mixer sensor new device]
- Added: [Comments in code]
- Added: [Configuration in project code style by HA rules]

## [v0.3.1] 2023-12-
- Rename `tempCWU` sensor name from 'water temperature' to 'HUW temperature'
- Rename  `pumpCO` binary_sensor name from `Pump` to `Boiler pump`



