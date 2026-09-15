# 📍 Embedded-GPS-tracker

> Fast, modular GPS tracking utility for real-time coordinate parsing, speed metrics, and location logging.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/Kebabist/Embedded-GPS-tracker/blob/main/LICENSE)
[![Status: Active](https://img.shields.io/badge/status-active-brightgreen.svg)]()

---

## 📖 Overview

Embedded-GPS-tracker is a lightweight toolkit for reading, parsing, and processing GPS telemetry and controlling a simple navigation server/client pair. The primary runnable scripts in this repository are:

- Navserver.py — navigation server that reads GPS input (serial), computes bearing/distance, and sends status updates to a client; it also contains thruster control helper functions.
- ClientPy — simple TCP client that connects to the server to set a destination and receive navigation updates.

This README documents how to run those scripts, the required dependencies, and how to run the included examples.

## ✨ Key Features

- NMEA parsing and simple navigation helpers (distance / bearing) using GeographicLib.
- Server/client pattern for remote control and status streaming.
- Thruster control helper functions and simple serial command protocol (adjust for your hardware).
- Small-footprint Python code that can run on embedded Linux devices (Raspberry Pi) or development machines.

## 🛠️ Supported Platforms & Requirements

- Languages: Python 3.8+.
- Hardware: Any GPS module that emits NMEA sentences over UART/Serial (e.g., u-blox NEO-6M/8M).
- Typical Python dependencies:
  - pyserial
  - geographiclib
  - numpy (optional, for smoothing/metrics)

Install Python dependencies:

```bash
pip install pyserial geographiclib
# Or use requirements.txt if provided:
python -m pip install -r requirements.txt
```

## 🚀 Quickstart (Run the server + client)

1. Connect your GPS module to a serial port (e.g., /dev/ttyUSB0, COM3).
2. Start the navigation server (accepts client connections on TCP port 5000 by default):

```bash
python Navserver.py
```

3. Start the client UI (interactive):

```bash
python ClientPy
```

Notes:
- Navserver.py currently uses a serial.Serial('COM4', baudrate=115200, timeout=1) by default (see Navserver.py: __init__). Edit that line to match your OS/port (e.g., '/dev/ttyUSB0' on Linux).
- For testing without hardware, Navserver.py contains commented alternative lines: you can either comment out the serial.Serial(...) line or replace it with a dummy fixed coordinate for quick tests.

## 📚 Programmatic Usage

Server example:

```python
from Navserver import NavigationServer

server = NavigationServer(host='0.0.0.0', port=5000)
server.start()  # blocks — same behavior as running `python Navserver.py`
```

Client example:

```python
from ClientPy import NavigationClient

client = NavigationClient('localhost', 5000)
client.connect()
client.set_destination(31.835928, 54.354836)
```

If you intend to reuse parsing logic as a library, consider refactoring parser functions/classes into a package (e.g., tracker/) and providing a minimal API surface.

## 🔧 Configuration & Tuning

- Sampling rate: control how many parsed messages are persisted vs. skipped.
- Filters: discard points with no fix, low satellite count, or very old timestamps.
- Output formatting: numeric precision, timezones (store in UTC by default).
- Serial port: change the hard-coded port inside Navserver.py or add a small CLI wrapper / environment variable to make this configurable.
- Thruster/Arduino comms: Navserver.py writes thruster commands to the Arduino serial connection. When testing without Arduino, comment out send_thruster_command/control_thrusters calls or replace serial with a mock.

## 🧪 Testing and Validation

- Add unit tests for the parser using recorded NMEA logs (place fixtures in tests/fixtures).
- Validate coordinate conversions and speed/bearing calculations against known-good examples.

Example files and demo (if present in the repo):

- examples/nmea_samples/*.nmea — example NMEA logs (fixtures)
- examples/demo/read_and_parse.py — small demo that attempts to use the repo parser and falls back to a tiny GPRMC parser for smoke tests

Run the demo (if examples/ is present):

```bash
python examples/demo/read_and_parse.py
```

## 🛠️ Contributing

Contributions are welcome! Please:

1. Fork the repo and create a branch for your feature/fix.
2. Open a Pull Request with a clear description and tests where applicable.
3. Follow the existing code style and add documentation for new features.

Consider adding:
- Example wiring diagrams for common modules (NEO-6M), e.g., in docs/hardware.md
- A Dockerfile or Vagrant box for reproducible development/testing environments.

## 🔒 License

This project is licensed under the MIT License — see the repository LICENSE file for details:

- https://github.com/Kebabist/Embedded-GPS-tracker/blob/main/LICENSE

## 🙋 Contact / Author

Maintainer: Kebabist

If you find issues or want to propose features, please open an issue on GitHub.
