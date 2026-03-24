import os
import socket
from datetime import datetime, timezone
from pathlib import Path

import requests
from flask import Flask, jsonify, render_template, request
from waitress import serve

BASE_DIR = Path(__file__).resolve().parent
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)

SERVICE_NAME = os.environ.get("HOUSE_GOBLIN_NAME", "house-goblin-api")
HOSTNAME_HINT = os.environ.get("HOUSE_GOBLIN_HOST", "house-goblin.local")
HOUSE_GOBLIN_PORT = os.environ.get("HOUSE_GOBLIN_PORT", "8787")
NTFY_PORT = os.environ.get("HOUSE_GOBLIN_NTFY_PORT", os.environ.get("NTFY_PORT", "2586"))
NTFY_BASE_URL = os.environ.get("NTFY_BASE_URL", f"http://127.0.0.1:{NTFY_PORT}").rstrip("/")
SUBTITLE = os.environ.get(
    "HOUSE_GOBLIN_SUBTITLE",
    "Tiny household goblin brain for your home Wi-Fi",
)


def read_uptime():
    try:
        with open("/proc/uptime", "r", encoding="utf-8") as handle:
            uptime_seconds = float(handle.read().split()[0])
    except (FileNotFoundError, ValueError, OSError):
        return None

    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    return {
        "seconds": int(uptime_seconds),
        "pretty": f"{days}d {hours}h {minutes}m",
    }


def build_dashboard_links():
    app_base = f"http://{HOSTNAME_HINT}:{HOUSE_GOBLIN_PORT}"
    ntfy_base = f"http://{HOSTNAME_HINT}:{NTFY_PORT}"
    return [
        {
            "name": "ntfy",
            "href": ntfy_base,
            "description": "Self-hosted house notifications",
            "kind": "live",
        },
        {
            "name": "goblin api health",
            "href": f"{app_base}/health",
            "description": "Tiny helper service heartbeat",
            "kind": "live",
        },
        {
            "name": "future movies/media box",
            "href": f"{app_base}/status",
            "description": "Reserved for a cozy little media shelf",
            "kind": "future",
        },
        {
            "name": "future rom launcher",
            "href": f"{app_base}/status",
            "description": "Placeholder for game-launching mischief",
            "kind": "future",
        },
        {
            "name": "future freezer alert",
            "href": f"{app_base}/status",
            "description": "Future cold-food panic button",
            "kind": "future",
        },
        {
            "name": "future family board",
            "href": f"{app_base}/status",
            "description": "Future chores, notes, and household scribbles",
            "kind": "future",
        },
    ]


def ntfy_health():
    try:
        response = requests.get(NTFY_BASE_URL, timeout=2)
        return response.ok
    except requests.RequestException:
        return False


@app.get("/")
def index():
    return render_template(
        "index.html",
        title="House Goblin",
        subtitle=SUBTITLE,
        links=build_dashboard_links(),
        hostname=socket.gethostname(),
        current_time=datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
        uptime=read_uptime(),
        ntfy_ok=ntfy_health(),
    )


@app.get("/health")
def health():
    return jsonify({"ok": True, "service": SERVICE_NAME})


@app.get("/status")
def status():
    return jsonify(
        {
            "ok": True,
            "service": SERVICE_NAME,
            "hostname": socket.gethostname(),
            "current_time": datetime.now(timezone.utc).astimezone().isoformat(),
            "uptime": read_uptime(),
            "configured_services": {
                "dashboard": f"http://{HOSTNAME_HINT}:{HOUSE_GOBLIN_PORT}",
                "ntfy": f"http://{HOSTNAME_HINT}:{NTFY_PORT}",
            },
            "ntfy_reachable": ntfy_health(),
            "note": "Local-only helper endpoints for House Goblin.",
        }
    )


@app.post("/notify")
def notify():
    payload = request.get_json(silent=True) or {}
    topic = str(payload.get("topic", "house")).strip() or "house"
    title = str(payload.get("title", "house goblin")).strip() or "house goblin"
    message = str(payload.get("message", "")).strip()

    if not message:
        return jsonify({"ok": False, "error": "message is required"}), 400

    headers = {"Title": title}

    try:
        response = requests.post(
            f"{NTFY_BASE_URL}/{topic}",
            data=message.encode("utf-8"),
            headers=headers,
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return (
            jsonify(
                {
                    "ok": False,
                    "error": "failed to forward to ntfy",
                    "detail": str(exc),
                }
            ),
            502,
        )

    return jsonify(
        {
            "ok": True,
            "forwarded_to": f"{NTFY_BASE_URL}/{topic}",
            "topic": topic,
            "title": title,
            "message": message,
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("HOUSE_GOBLIN_PORT", "8787"))
    serve(app, host="0.0.0.0", port=port)
