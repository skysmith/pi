#!/usr/bin/env python3
"""Drive the RC tank from a Linux joystick device.

This is intended for the Pi-side 8BitDo Ultimate 2C receiver path that showed
up as `/dev/input/js0` under the `xpad` driver.
"""

from __future__ import annotations

import argparse
import os
import select
import signal
import struct
import time
from dataclasses import dataclass

from rc_tank import DryRunBackend, GpioZeroBackend, MotorBackend, RCTankController, mix_arcade_drive

JS_EVENT_BUTTON = 0x01
JS_EVENT_AXIS = 0x02
JS_EVENT_INIT = 0x80
JS_EVENT_FORMAT = "IhBB"
JS_EVENT_SIZE = struct.calcsize(JS_EVENT_FORMAT)


@dataclass
class GamepadState:
    throttle: float = 0.0
    steering: float = 0.0
    turbo: bool = False
    stop_pressed: bool = False


class JoystickReader:
    def __init__(self, device_path: str) -> None:
        self.device_path = device_path
        self.fd = os.open(device_path, os.O_RDONLY | os.O_NONBLOCK)

    def fileno(self) -> int:
        return self.fd

    def close(self) -> None:
        os.close(self.fd)

    def read_events(self) -> list[tuple[int, int, int]]:
        events: list[tuple[int, int, int]] = []
        while True:
            try:
                payload = os.read(self.fd, JS_EVENT_SIZE)
            except BlockingIOError:
                break

            if not payload:
                raise EOFError("Joystick disconnected")
            if len(payload) != JS_EVENT_SIZE:
                continue

            _, value, event_type, number = struct.unpack(JS_EVENT_FORMAT, payload)
            event_type &= ~JS_EVENT_INIT
            events.append((event_type, number, value))
        return events


def normalize_axis(value: int, deadzone: float) -> float:
    normalized = max(-1.0, min(1.0, value / 32767.0))
    if abs(normalized) < deadzone:
        return 0.0
    return normalized


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Drive the RC tank from a USB gamepad")
    parser.add_argument(
        "--device",
        default="/dev/input/js0",
        help="Joystick device path, default: /dev/input/js0",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print drive updates without touching GPIO",
    )
    parser.add_argument(
        "--deadzone",
        type=float,
        default=0.15,
        help="Ignore small axis movement, default: 0.15",
    )
    parser.add_argument(
        "--max-speed",
        type=float,
        default=0.75,
        help="Base max output scaling from 0.0 to 1.0, default: 0.75",
    )
    parser.add_argument(
        "--turbo-scale",
        type=float,
        default=1.0,
        help="Max output scaling while turbo is held, default: 1.0",
    )
    parser.add_argument(
        "--poll-ms",
        type=int,
        default=20,
        help="Loop interval in milliseconds, default: 20",
    )
    return parser.parse_args()


def choose_backend(dry_run: bool) -> MotorBackend:
    return DryRunBackend() if dry_run else GpioZeroBackend()


def update_state(state: GamepadState, event_type: int, number: int, value: int, deadzone: float) -> bool:
    changed = False

    if event_type == JS_EVENT_AXIS:
        # This 8BitDo reports left stick vertical on axis 0 and horizontal on axis 1.
        if number == 0:
            throttle = normalize_axis(value, deadzone)
            changed = throttle != state.throttle
            state.throttle = throttle
        elif number == 1:
            steering = -normalize_axis(value, deadzone)
            changed = steering != state.steering
            state.steering = steering
    elif event_type == JS_EVENT_BUTTON:
        pressed = value != 0
        if number == 5:
            changed = pressed != state.turbo
            state.turbo = pressed
        elif number == 1:
            changed = pressed != state.stop_pressed
            state.stop_pressed = pressed

    return changed


def format_drive(left: float, right: float, scale: float, state: GamepadState) -> str:
    return (
        f"throttle={state.throttle:+.2f} steering={state.steering:+.2f} "
        f"left={left:+.2f} right={right:+.2f} scale={scale:.2f} "
        f"turbo={'on' if state.turbo else 'off'}"
    )


def main() -> int:
    args = parse_args()
    backend = choose_backend(args.dry_run)
    controller = RCTankController(backend=backend)
    joystick = JoystickReader(args.device)
    state = GamepadState()
    running = True
    last_report = ""

    def handle_exit(_signum: int, _frame: object) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    controller.initialize()
    print(f"RC tank gamepad mode on {args.device}")
    print("left stick: drive, RB: turbo, B: stop, Ctrl-C: exit")

    try:
        while running:
            ready, _, _ = select.select([joystick.fileno()], [], [], max(0, args.poll_ms) / 1000.0)
            state_changed = False

            if ready:
                for event_type, number, value in joystick.read_events():
                    if update_state(state, event_type, number, value, args.deadzone):
                        state_changed = True

            if state.stop_pressed:
                left = 0.0
                right = 0.0
            else:
                left, right = mix_arcade_drive(state.throttle, state.steering)
                left, right = right, left

            scale = args.turbo_scale if state.turbo else args.max_speed
            scale = max(0.0, min(1.0, scale))
            left *= scale
            right *= scale
            controller.drive(left, right)

            report = format_drive(left, right, scale, state)
            if state_changed and report != last_report:
                print(report)
                last_report = report
    except EOFError:
        print("Joystick disconnected, stopping motors.")
    finally:
        controller.shutdown()
        joystick.close()
        if isinstance(backend, DryRunBackend):
            print("backend events:")
            for event in backend.events:
                print(f"  - {event}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
