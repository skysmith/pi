# House Goblin

House Goblin is now a Pi-native, no-Docker local dashboard project for a Raspberry Pi Zero 2 W. Instead of running a container stack, it keeps things lighter:

- one small Flask app serves the front-door website and helper API
- `ntfy` runs as a native binary on the Pi
- shell scripts handle bootstrap, start, stop, restart, logs, and test notifications

That is a much better fit for a Zero 2 W than a full container setup. The goal is the same tiny household goblin brain, just with less overhead and less ceremony.

## Why This Plan Changed

The repo was first sketched as a Docker Compose stack, but your Pi does not have Docker installed and the Zero 2 W only has modest RAM. For this hardware, a direct-run service model is more realistic:

- lower memory overhead
- faster startup
- easier debugging from the Pi terminal
- fewer moving parts to maintain

## Ports

- House Goblin dashboard and API: `8787`
- ntfy: `2586`

The dashboard is the front door now, so there is no separate Homepage service.

## File Structure

```text
.
├── .env.example
├── .gitignore
├── README.md
├── PROJECT.md
├── cad/
│   ├── README.md
│   └── pi_sensor_tank_v1.scad
├── config/
│   └── ntfy/
│       └── server.yml
├── docs/
│   ├── CURRENT_PHYSICAL_SETUP.md
│   ├── PI_SENSOR_TANK_V1.md
│   └── assets/
├── exports/
│   └── pi-sensor-tank-v1/
├── ops/
│   └── systemd/
│       └── house-goblin.service
├── scripts/
│   ├── bootstrap.sh
│   ├── down.sh
│   ├── logs.sh
│   ├── notify.sh
│   ├── rc_tank.py
│   ├── restart.sh
│   └── up.sh
└── services/
    └── goblin-api/
        ├── app.py
        ├── requirements.txt
        ├── static/
        │   └── style.css
        └── templates/
            └── index.html
```

## Prerequisites

- Raspberry Pi Zero 2 W on the same Wi-Fi as your phone or laptop
- Python 3 and `python3-venv`
- `curl`
- `ntfy` installed natively on the Pi
- optional but nice: mDNS/Bonjour so `house-goblin.local` resolves on your network

Check the Pi basics:

```bash
uname -a
free -h
python3 --version
```

If memory is already very tight before starting anything, keep future add-ons small and avoid background clutter.

## Install ntfy

The official ntfy docs currently support Linux arm64 via either the native package repository or the release tarball, and note that `ntfy serve` or `systemctl start ntfy` are the normal startup paths. This README uses the package-repo path because it is the easiest to keep updated.

On a 64-bit Pi OS or Debian install:

```bash
sudo mkdir -p /etc/apt/keyrings
sudo curl -L -o /etc/apt/keyrings/ntfy.gpg https://archive.ntfy.sh/apt/keyring.gpg
sudo apt install -y apt-transport-https
echo "deb [arch=arm64 signed-by=/etc/apt/keyrings/ntfy.gpg] https://archive.ntfy.sh/apt stable main" | sudo tee /etc/apt/sources.list.d/ntfy.list
sudo apt update
sudo apt install -y ntfy
```

If your Pi is `armhf` instead of `arm64`, change the `arch=` value in the apt source line accordingly.

This project runs `ntfy` directly from `./scripts/up.sh`, using the repo config at `config/ntfy/server.yml`, so you do not need to set up a system service for ntfy in v1.

## Bootstrap House Goblin

Copy the example environment file:

```bash
cp .env.example .env
```

Note: values with spaces, like `HOUSE_GOBLIN_SUBTITLE`, are intentionally quoted in `.env.example` so the shell scripts can safely source `.env`.

Install Python dependencies into a local virtualenv:

```bash
./scripts/bootstrap.sh
```

That creates `.venv/` and the local log/run folders under `var/`.

## Run It

Start both `ntfy` and the House Goblin dashboard:

```bash
./scripts/up.sh
```

Stop it:

```bash
./scripts/down.sh
```

Restart it:

```bash
./scripts/restart.sh
```

Watch logs:

```bash
./scripts/logs.sh
```

Watch just one service:

```bash
./scripts/logs.sh goblin-api
./scripts/logs.sh ntfy
```

## Test Each Piece

Check the dashboard from the Pi:

```bash
curl http://127.0.0.1:8787/
```

Check the helper API:

```bash
curl http://127.0.0.1:8787/health
curl http://127.0.0.1:8787/status
```

Check ntfy directly:

```bash
curl http://127.0.0.1:2586
```

Send a direct ntfy test:

```bash
curl -d "front door test" -H "Title: House Goblin" http://127.0.0.1:2586/house
```

Send a notification through House Goblin:

```bash
./scripts/notify.sh "temp too high" "freezer" "house"
```

Or call the endpoint directly:

```bash
curl -X POST http://127.0.0.1:8787/notify \
  -H "Content-Type: application/json" \
  -d '{"topic":"house","title":"freezer","message":"temp too high"}'
```

## Open It From Another Device On The Same Wi-Fi

Try:

- `http://house-goblin.local:8787/`
- `http://house-goblin.local:2586/`

If `.local` discovery does not work, get the Pi IP:

```bash
hostname -I
```

Then use:

- `http://PI_IP:8787/`
- `http://PI_IP:2586/`

## Verified Bring-Up

House Goblin has now been brought up successfully on the Pi itself.

- Repo location on Pi: `/opt/house-goblin`
- Verified dashboard URL: `http://house-goblin.local:8787/`
- Verified fallback URL: `http://192.168.0.232:8787/`
- Verified ntfy URL: `http://house-goblin.local:2586/`

The Pi hostname was updated from `raspberrypi` to `house-goblin` so Bonjour / mDNS resolves `house-goblin.local` on the local network.

## Dashboard Features

The House Goblin front page now lives inside the Flask app itself. It shows:

- the title `House Goblin`
- a playful subtitle
- a small live status strip for hostname, time, uptime, and ntfy reachability
- tiles for:
  - ntfy
  - goblin api health
  - future movies/media box
  - future rom launcher
  - future freezer alert
  - future family board

Those future tiles point to the local `/status` page for now.

## Optional Boot Persistence

If you want House Goblin to start on boot later, a sample systemd unit is included at:

- `ops/systemd/house-goblin.service`

It assumes the project lives at `/opt/house-goblin` and runs as user `pi`. Adjust the paths if you keep the repo elsewhere.

## Extend It Later

Good next steps that still respect the Pi:

- add one more small endpoint in `services/goblin-api/app.py`
- add a new tile in `services/goblin-api/templates/index.html`
- wire a shell script to publish alerts into ntfy
- keep everything file-based and lightweight for as long as possible
- remix the tracked robot upper body using the CAD in `cad/`

Avoid heavy extras unless the Pi gets upgraded.

## Robot Packaging

The repo now includes a packaging-first CAD pass for a compact tracked Pi robot:

- [PI sensor tank v1 notes](/Users/sky/Documents/codex/lab/pi/docs/PI_SENSOR_TANK_V1.md)
- [CAD guide](/Users/sky/Documents/codex/lab/pi/cad/README.md)
- [OpenSCAD source](/Users/sky/Documents/codex/lab/pi/cad/pi_sensor_tank_v1.scad)

This v1 design assumes:

- tracked N20 lower chassis
- Pi Zero 2 W
- TB6612 motor driver
- 1S 2000mAh battery
- USB-C charge/protection board
- front-facing sensor bay
- no MG90S servo mounts

Exported STL files currently live in:

- [deck.stl](/Users/sky/Documents/codex/lab/pi/exports/pi-sensor-tank-v1/deck.stl)
- [lid.stl](/Users/sky/Documents/codex/lab/pi/exports/pi-sensor-tank-v1/lid.stl)
- [sensor_plate.stl](/Users/sky/Documents/codex/lab/pi/exports/pi-sensor-tank-v1/sensor_plate.stl)
- [charger_bracket.stl](/Users/sky/Documents/codex/lab/pi/exports/pi-sensor-tank-v1/charger_bracket.stl)

## Print Workflow

Current printing workflow for this project:

- printer: `Flashforge Adventurer 5M Pro`
- slicer / send workflow: `Orca-Flashforge`
- handoff format from this repo: `STL`
- printing is currently manual: Codex prepares CAD and STL files, and the user handles slicing, printer setup, and print start from Orca-Flashforge

Practical implication:

- prefer small-bed-friendly parts
- prefer separate printable components over one-piece bodies
- keep export bundles organized and clearly named
- do not assume direct printer control or unattended print submission from this repo

## RC Tank Bring-Up

The repo now includes a real Raspberry Pi GPIO smoke test at:

- [scripts/rc_tank.py](/Users/sky/Documents/codex/lab/pi/scripts/rc_tank.py)

Confirmed working tank mapping:

- `PWMA -> GPIO12`
- `AIN1 -> GPIO5`
- `AIN2 -> GPIO6`
- `STBY -> GPIO16`
- `BIN1 -> GPIO23`
- `BIN2 -> GPIO24`
- `PWMB -> GPIO13`

The real smoke test was run successfully on the Pi with this mapping and is now the only motor mapping kept in the project.

For live gamepad control on the Pi, use:

```bash
python3 scripts/rc_tank_gamepad.py
```

Current controller notes for the confirmed 2.4G receiver path:

- default joystick device: `/dev/input/js0`
- stable event path: `/dev/input/by-id/usb-8BitDo_8BitDo_Ultimate_2C_Wireless_Controller_F53A52260F-event-joystick`
- stable joystick path: `/dev/input/by-id/usb-8BitDo_8BitDo_Ultimate_2C_Wireless_Controller_F53A52260F-joystick`
- left stick drives throttle and steering
- calibrated stick behavior:
  - up: forward
  - down: reverse
  - left: left turn
  - right: right turn
- `RB` enables turbo scaling
- `B` forces stop while held

If you want to test the mapping without touching GPIO from another machine, run:

```bash
python3 scripts/rc_tank_gamepad.py --dry-run
```

Practical notes from live Pi testing:

- the controller was successfully detected on the Pi over the `2.4G` receiver path
- active controller mode showed up as USB product `8BitDo Ultimate 2C Wireless Controller`
- the receiver can also fall back to an `8BitDo IDLE` USB mode until the controller reconnects
- a conservative first-drive command that worked well was:

```bash
python3 scripts/rc_tank_gamepad.py --max-speed 0.4
```

## Controller Choice

Current controller purchase for this project:

- `8BitDo Ultimate 2C Wireless Controller`
- Amazon item: `B0D6BF69X4`

Current intent:

- use one controller with the Pi robot
- use the others for N64 emulation on macOS machines

Current confirmed state for the Pi robot:

- the `2.4G` receiver path works on the Pi
- Bluetooth support on the Pi is still unconfirmed

This controller is now the default gamepad candidate for the robot control path unless later testing forces a change.

## Physical Setup References

Current hardware photo references live in:

- [CURRENT_PHYSICAL_SETUP.md](/Users/sky/Documents/codex/lab/pi/docs/CURRENT_PHYSICAL_SETUP.md)

That doc now tracks:

- the current overall robot physical setup image
- the separate charge-board reference image
- the latest assumptions for packaging and wiring

## Honest Caveats

- This repo was rewritten from a shell that is currently on macOS, but the current `8BitDo` receiver path and `scripts/rc_tank_gamepad.py` flow have now been exercised against the live Pi robot.
- `ntfy` installation steps in this README are based on the official ntfy install docs and repository instructions, which currently point Debian and Ubuntu users to `archive.ntfy.sh`.
- If the Pi is 32-bit instead of 64-bit, use the `armhf` ntfy package instructions instead of `arm64`.

Official references used for the ntfy install notes:

- [ntfy install docs](https://docs.ntfy.sh/install/)
- [ntfy config docs](https://docs.ntfy.sh/config/)
