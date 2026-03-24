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
├── config/
│   └── ntfy/
│       └── server.yml
├── ops/
│   └── systemd/
│       └── house-goblin.service
├── scripts/
│   ├── bootstrap.sh
│   ├── down.sh
│   ├── logs.sh
│   ├── notify.sh
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

Avoid heavy extras unless the Pi gets upgraded.

## Honest Caveats

- This repo was rewritten from a shell that is currently on macOS, not directly on the Pi, so the code and scripts were sanity-checked here but not fully exercised on the real hardware in this session.
- `ntfy` installation steps in this README are based on the official ntfy install docs and repository instructions, which currently point Debian and Ubuntu users to `archive.ntfy.sh`.
- If the Pi is 32-bit instead of 64-bit, use the `armhf` ntfy package instructions instead of `arm64`.

Official references used for the ntfy install notes:

- [ntfy install docs](https://docs.ntfy.sh/install/)
- [ntfy config docs](https://docs.ntfy.sh/config/)
