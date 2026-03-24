# Pi Sensor Tank CAD

This folder contains a printable v1 upper-structure remix for the tracked N20 tank direction.

The design assumes the lower drivetrain comes from an existing small tracked N20 chassis, while these parts handle packaging:

- `deck`: electronics tray / mid deck
- `lid`: removable vented service cover
- `sensor_plate`: front modular sensor face
- `charger_bracket`: simple charger/protection board holder

## Source

- Main CAD source: `pi_sensor_tank_v1.scad`

## Default Packaging Assumptions

- 2x N20 1909_30 3V motors in the lower hull
- Pi Zero 2 W on the upper right deck
- TB6612-style motor driver on the upper left/rear area
- 1S 2000mAh battery low and central in the tray
- USB-C charge/protection board mounted near the side wall with external access
- front area reserved for future sensors instead of servos

## Confirmed Drive Mapping

- `PWMA -> GPIO12`
- `AIN1 -> GPIO5`
- `AIN2 -> GPIO6`
- `STBY -> GPIO16`
- `BIN1 -> GPIO23`
- `BIN2 -> GPIO24`
- `PWMB -> GPIO13`

## Print Guidance

- Printer target: small bed
- Suggested layer height: `0.20 mm`
- Suggested walls: `3`
- Suggested infill: `15-20%`
- Print `deck` and `lid` flat on the bed
- Print `sensor_plate` upright only if your printer handles thin tall parts well; otherwise lay it flat

## OpenSCAD Usage

Preview the full kit:

```bash
openscad /Users/sky/Documents/codex/lab/pi/cad/pi_sensor_tank_v1.scad
```

Export one part at a time:

```bash
openscad -D 'part="deck"' -o deck.stl /Users/sky/Documents/codex/lab/pi/cad/pi_sensor_tank_v1.scad
openscad -D 'part="lid"' -o lid.stl /Users/sky/Documents/codex/lab/pi/cad/pi_sensor_tank_v1.scad
openscad -D 'part="sensor_plate"' -o sensor_plate.stl /Users/sky/Documents/codex/lab/pi/cad/pi_sensor_tank_v1.scad
openscad -D 'part="charger_bracket"' -o charger_bracket.stl /Users/sky/Documents/codex/lab/pi/cad/pi_sensor_tank_v1.scad
```

## Notes

- This is a packaging-first v1, not a full lower-chassis replacement.
- It intentionally leaves out MG90S mounts.
- The front plate uses generic slots so it can be adapted for ToF, ultrasonic, bumper, or line sensors later.
