#!/usr/bin/env python3
"""Safe RC tank motor mapping smoke test.

This module defaults to a dry-run backend so it can be exercised from a
development machine without touching hardware. If gpiozero is available on a
Raspberry Pi, pass --real to drive the configured pins for short intervals.
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from typing import Dict, List, Protocol


@dataclass(frozen=True)
class TankPins:
    left_forward: int = 5
    left_reverse: int = 6
    right_forward: int = 13
    right_reverse: int = 19
    pwm_left: int = 12
    pwm_right: int = 18
    standby: int = 26


class MotorBackend(Protocol):
    def setup(self, pins: TankPins) -> None: ...

    def set_digital(self, pin: int, value: bool) -> None: ...

    def set_pwm(self, pin: int, duty_cycle: float) -> None: ...

    def cleanup(self) -> None: ...


class DryRunBackend:
    """Records GPIO transitions instead of touching hardware."""

    def __init__(self) -> None:
        self.events: List[str] = []
        self.digital: Dict[int, bool] = {}
        self.pwm: Dict[int, float] = {}

    def setup(self, pins: TankPins) -> None:
        self.events.append(f"setup pins={pins}")

    def set_digital(self, pin: int, value: bool) -> None:
        self.digital[pin] = value
        self.events.append(f"digital pin={pin} value={'HIGH' if value else 'LOW'}")

    def set_pwm(self, pin: int, duty_cycle: float) -> None:
        bounded = max(0.0, min(1.0, duty_cycle))
        self.pwm[pin] = bounded
        self.events.append(f"pwm pin={pin} duty={bounded:.2f}")

    def cleanup(self) -> None:
        self.events.append("cleanup")


class GpioZeroBackend:
    """Real Raspberry Pi backend using gpiozero."""

    def __init__(self) -> None:
        try:
            from gpiozero import DigitalOutputDevice, PWMOutputDevice
        except ImportError as exc:  # pragma: no cover
            raise SystemExit(
                "gpiozero is not installed. Re-run without --real or install gpiozero on the Pi."
            ) from exc

        self._digital_cls = DigitalOutputDevice
        self._pwm_cls = PWMOutputDevice
        self._digital: Dict[int, object] = {}
        self._pwm: Dict[int, object] = {}

    def setup(self, pins: TankPins) -> None:
        for pin in [
            pins.left_forward,
            pins.left_reverse,
            pins.right_forward,
            pins.right_reverse,
            pins.standby,
        ]:
            self._digital[pin] = self._digital_cls(pin, active_high=True, initial_value=False)
        for pin in [pins.pwm_left, pins.pwm_right]:
            self._pwm[pin] = self._pwm_cls(pin, initial_value=0.0)

    def set_digital(self, pin: int, value: bool) -> None:
        device = self._digital[pin]
        if value:
            device.on()
        else:
            device.off()

    def set_pwm(self, pin: int, duty_cycle: float) -> None:
        self._pwm[pin].value = max(0.0, min(1.0, duty_cycle))

    def cleanup(self) -> None:
        for device in self._digital.values():
            device.off()
            device.close()
        for device in self._pwm.values():
            device.value = 0.0
            device.close()


class RCTankController:
    def __init__(self, backend: MotorBackend, pins: TankPins | None = None) -> None:
        self.backend = backend
        self.pins = pins or TankPins()

    def initialize(self) -> None:
        self.backend.setup(self.pins)
        self.backend.set_digital(self.pins.standby, True)
        self.stop()

    def stop(self) -> None:
        self.backend.set_digital(self.pins.left_forward, False)
        self.backend.set_digital(self.pins.left_reverse, False)
        self.backend.set_digital(self.pins.right_forward, False)
        self.backend.set_digital(self.pins.right_reverse, False)
        self.backend.set_pwm(self.pins.pwm_left, 0.0)
        self.backend.set_pwm(self.pins.pwm_right, 0.0)

    def drive(self, left: float, right: float) -> None:
        self._set_side(
            forward_pin=self.pins.left_forward,
            reverse_pin=self.pins.left_reverse,
            pwm_pin=self.pins.pwm_left,
            value=left,
        )
        self._set_side(
            forward_pin=self.pins.right_forward,
            reverse_pin=self.pins.right_reverse,
            pwm_pin=self.pins.pwm_right,
            value=right,
        )

    def shutdown(self) -> None:
        self.stop()
        self.backend.set_digital(self.pins.standby, False)
        self.backend.cleanup()

    def _set_side(self, forward_pin: int, reverse_pin: int, pwm_pin: int, value: float) -> None:
        bounded = max(-1.0, min(1.0, value))
        if bounded > 0:
            self.backend.set_digital(forward_pin, True)
            self.backend.set_digital(reverse_pin, False)
            self.backend.set_pwm(pwm_pin, bounded)
            return
        if bounded < 0:
            self.backend.set_digital(forward_pin, False)
            self.backend.set_digital(reverse_pin, True)
            self.backend.set_pwm(pwm_pin, abs(bounded))
            return
        self.backend.set_digital(forward_pin, False)
        self.backend.set_digital(reverse_pin, False)
        self.backend.set_pwm(pwm_pin, 0.0)


def smoke_test(controller: RCTankController, pause_s: float) -> List[str]:
    sequence = [
        ("forward", 0.60, 0.60),
        ("reverse", -0.45, -0.45),
        ("pivot_left", -0.40, 0.40),
        ("pivot_right", 0.40, -0.40),
        ("creep_left_track", 0.25, 0.00),
        ("creep_right_track", 0.00, 0.25),
        ("stop", 0.00, 0.00),
    ]

    events: List[str] = []
    controller.initialize()
    events.append(f"initialized standby pin {controller.pins.standby}")
    for name, left, right in sequence:
        controller.drive(left, right)
        events.append(
            f"{name}: left={left:+.2f} via pins "
            f"{controller.pins.left_forward}/{controller.pins.left_reverse}/{controller.pins.pwm_left}, "
            f"right={right:+.2f} via pins "
            f"{controller.pins.right_forward}/{controller.pins.right_reverse}/{controller.pins.pwm_right}"
        )
        time.sleep(pause_s)
    controller.shutdown()
    events.append("shutdown complete")
    return events


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RC tank motor mapping smoke test")
    parser.add_argument(
        "--real",
        action="store_true",
        help="Use gpiozero and touch real Raspberry Pi GPIO pins",
    )
    parser.add_argument(
        "--pause-ms",
        type=int,
        default=150,
        help="Delay between test steps in milliseconds",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    backend: MotorBackend = GpioZeroBackend() if args.real else DryRunBackend()
    controller = RCTankController(backend=backend)
    events = smoke_test(controller, pause_s=max(0, args.pause_ms) / 1000.0)

    print("RC tank smoke test")
    print(f"mode: {'REAL GPIO' if args.real else 'DRY RUN'}")
    print(f"pins: {controller.pins}")
    print("sequence:")
    for event in events:
        print(f"  - {event}")

    if isinstance(backend, DryRunBackend):
        print("backend events:")
        for event in backend.events:
            print(f"  - {event}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
