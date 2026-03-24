# House Goblin GPIO Sketch

This is a future-facing sketch for turning House Goblin into a small GPIO control hub on the Raspberry Pi Zero 2 W.

It is not implemented yet. The goal is to capture a practical direction for later without locking us into unnecessary complexity now.

## Big Idea

House Goblin could grow from a local dashboard plus helper API into a tiny household control surface for:

- indicator LEDs
- relays
- buzzers
- buttons
- sensors
- motor drivers
- simple robot projects like a tiny RC car

The same local web UI could become the front door for both home tools and hardware toys.

## Guiding Principles

- keep everything local-only on house Wi-Fi
- prefer boring, safe GPIO patterns over clever hacks
- never drive motors, relays, or other loads directly from Pi GPIO pins
- use a driver board or transistor stage for anything beyond tiny logic signals
- default to safe startup states
- make motion or power outputs time-limited unless explicitly held alive

## Good First GPIO Features

The safest early additions would be:

- read-only GPIO status page
- toggle one LED on and off
- trigger a buzzer or small indicator
- read a button or simple digital sensor
- publish ntfy alerts when a sensor changes state

Those let House Goblin become useful for experiments without immediately jumping into motor control.

## Future API Shape

Possible future endpoints:

- `GET /gpio/status`
  Returns configured pins, modes, and current values.

- `POST /gpio/pin/<name>/on`
  Sets a named output high.

- `POST /gpio/pin/<name>/off`
  Sets a named output low.

- `POST /gpio/pin/<name>/pulse`
  Turns an output on briefly, then off again.

- `POST /car/arm`
  Enables movement controls for a short session.

- `POST /car/drive`
  Accepts left and right motor power values plus a short timeout.

- `POST /car/stop`
  Immediately stops all motion outputs.

## Suggested Config Model

If we add GPIO later, a small config file would keep pin assignments out of the main app code.

Example shape:

```yaml
pins:
  status_led:
    bcm: 17
    mode: output
    safe_state: low

  horn:
    bcm: 27
    mode: output
    safe_state: low

car:
  enabled: false
  driver: tb6612fng
  left_forward: 5
  left_reverse: 6
  right_forward: 23
  right_reverse: 24
  pwm_left: 12
  pwm_right: 13
  standby: 16
  max_duty_cycle: 0.7
  heartbeat_timeout_ms: 300
```

## RC Car Direction

A tiny RC car version of House Goblin is very realistic if the hardware is kept simple.

Recommended hardware pattern:

- Raspberry Pi Zero 2 W
- dual motor driver such as `TB6612FNG`
- separate battery or motor power source
- shared ground between Pi and motor driver
- optional small steering servo or differential drive setup

Recovered and confirmed working TB6612-style BCM mapping for this project:

- `PWMA -> GPIO12`
- `AIN1 -> GPIO5`
- `AIN2 -> GPIO6`
- `STBY -> GPIO16`
- `BIN1 -> GPIO23`
- `BIN2 -> GPIO24`
- `PWMB -> GPIO13`

Do not power motors from the Pi directly.

The Pi should only send logic-level control signals to a proper motor driver.

## Web UI Idea

A future RC control page could include:

- arm/disarm toggle
- big stop button
- directional pad for forward, reverse, left, right
- speed slider
- status block for battery, Wi-Fi strength, and last command time

For mobile use, the UI should favor:

- large touch targets
- minimal animations
- very short request paths
- clear visual armed vs disarmed state

## Safety Rules

If movement control is added later, these rules should be considered mandatory:

- all outputs default to safe off state on startup
- motor control remains disabled until manually armed
- any movement command expires automatically after a short timeout
- stop all outputs on process exit or exception
- expose one dedicated emergency stop action in the UI
- log every drive command while testing

## Library Options

Likely software choices on Raspberry Pi:

- `gpiozero` for simple high-level GPIO work
- `RPi.GPIO` or `lgpio` if lower-level control is needed
- possibly `pigpio` only if remote or more advanced timing becomes necessary

For the first version, `gpiozero` is probably the friendliest starting point.

## Phased Plan

Phase 1:

- add one LED output
- add one sensor input
- add `/gpio/status`
- add ntfy alert on sensor change

Phase 2:

- add named pin config file
- add safe output toggle endpoints
- add a small dashboard section for GPIO widgets

Phase 3:

- add motor driver abstraction
- add arm, drive, and stop endpoints
- add a touch-friendly RC control page

Phase 4:

- add camera streaming or snapshots
- add battery telemetry if hardware supports it
- add simple autonomous routines or timed actions

## Nice Future Uses Beyond A Car

The same GPIO foundation could later support:

- freezer alarm sensor
- door chime
- mailbox flag sensor
- family button board
- LED status panel
- tiny sprinkler or relay controller
- motion-triggered alerts

## Practical Constraints

The Pi Zero 2 W is capable, but still small:

- keep polling light
- avoid heavy video stacks unless truly needed
- prefer simple web actions over always-on complex services
- keep background loops modest

House Goblin can become a very fun little robot or home-control brain, but it should stay goblin-sized.
