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
- `exports/pi-sensor-tank-v1/deck.stl`
- `exports/pi-sensor-tank-v1/lid.stl`
- `exports/pi-sensor-tank-v1/sensor_plate.stl`
- `exports/pi-sensor-tank-v1/charger_bracket.stl`

## Current Print Setup

- Printer: `Flashforge Adventurer 5M Pro`
- Slicer: `Orca-Flashforge`
- Current workflow: STL export from this repo, then manual slicing and printing by the user

This means the CAD is intentionally handed off as printable parts rather than a fully automated slicer/project workflow.

## Current Control Hardware Choice

- Controller selected for robot testing: `8BitDo Ultimate 2C Wireless Controller`
- Amazon item reference: `B0D6BF69X4`

Current validated control state:

- the `2.4G` receiver path works on the Pi
- Bluetooth support is still experimental / unconfirmed
- live Pi-side drive control now uses `scripts/rc_tank_gamepad.py`
- confirmed default joystick node on the Pi: `/dev/input/js0`

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

## Confirmed Drivetrain Mapping

- `PWMA -> GPIO12`
- `AIN1 -> GPIO5`
- `AIN2 -> GPIO6`
- `STBY -> GPIO16`
- `BIN1 -> GPIO23`
- `BIN2 -> GPIO24`
- `PWMB -> GPIO13`

This mapping was recovered from older Pi-side motor-control work, then re-tested successfully on the live Pi with the current `scripts/rc_tank.py` smoke test.

## Confirmed Gamepad Control

- Controller: `8BitDo Ultimate 2C Wireless Controller`
- Receiver path confirmed: `2.4G USB receiver`
- Active USB product name on the Pi: `8BitDo Ultimate 2C Wireless Controller`
- A temporary fallback USB mode of `8BitDo IDLE` was also observed before the controller reconnected
- Current live-control entrypoint: `python3 scripts/rc_tank_gamepad.py --max-speed 0.4`
- Calibrated left-stick behavior:
  - up: forward
  - down: reverse
  - left: left turn
  - right: right turn
- Safety behavior:
  - `RB` enables turbo scaling
  - `B` forces stop while held
  - disconnect or `Ctrl-C` stops the motors

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
