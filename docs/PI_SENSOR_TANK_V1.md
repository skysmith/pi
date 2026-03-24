# Pi Sensor Tank V1

This is the first printable packaging pass for the confirmed tracked Pi robot.

## Goal

Turn the current overflowing tracked build into a clean enclosed robot body that:

- keeps the confirmed 2-motor tracked drivetrain
- encloses the Pi, battery, and motor driver
- exposes charging access externally
- leaves the front ready for future sensors
- avoids servo complexity in v1

## V1 Parts

- `cad/pi_sensor_tank_v1.scad`
- `cad/README.md`

The CAD splits the upper structure into:

- `deck`
- `lid`
- `sensor_plate`
- `charger_bracket`

## Layout Intent

- Battery sits low and near the center to improve stability.
- Pi Zero 2 W sits high enough for SD and cable access.
- TB6612 sits near the motor wire exit path to reduce cable mess.
- USB-C charging is intended to be exposed through a side cutout.
- Front face is modular for future sensors.

## Future Sensor Candidates

- VL53L0X / VL53L1X ToF
- HC-SR04 style ultrasonic module
- bumper switches
- small line sensor strip
- camera later, if enclosure height allows

## What V1 Deliberately Does Not Include

- MG90S servo mounts
- turret or pan/tilt head
- arm or gripper
- extra H-bridge outputs
- decorative shell complexity that blocks service access

## Validation Checklist

- N20 motors clear the lower chassis geometry
- Battery fits under the lid without pinching wires
- Pi remains removable without tearing down the drivetrain
- Charge port is reachable from outside the body
- Motor smoke test can still run with the body assembled
- Front sensor mounting area remains open for later upgrades
