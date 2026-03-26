# Pi Workspace

## Workspace Metadata

- Name: Pi Workspace
- Domain: lab
- Status: active
- Purpose: Notes, setup state, and operational context for the Raspberry Pi Zero 2 W on the local network
- Path: lab/pi
- Related:
  - lab/games
  - lab/media
  - lab/ai
- Tags:
  - raspberry-pi
  - retropie
  - hardware
  - ops
  - 3d-printing

This folder is intentionally lightweight right now.

It exists to track the Pi's current state, what has been attempted, and the practical commands needed to continue work without rediscovering the same setup details.

It also now tracks the printable enclosure work for the tracked Pi robot, with STL-first handoff for manual printing on a Flashforge Adventurer 5M Pro via Orca-Flashforge.

The current controller choice for the robot path is the 8BitDo Ultimate 2C Wireless Controller.

That controller has now been validated on the Pi over the `2.4G` receiver path, and the live drive script is `scripts/rc_tank_gamepad.py`.
