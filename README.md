# 📍 Embedded-GPS-tracker

> Fast, modular GPS tracking utility for real-time coordinate parsing, speed metrics, and location logging.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/Kebabist/Embedded-GPS-tracker/blob/main/LICENSE)
[![Status: Active](https://img.shields.io/badge/status-active-brightgreen.svg)]()

---

## 📖 Overview

Embedded-GPS-tracker is a lightweight, modular toolkit for reading, parsing, and processing GPS NMEA streams in resource-constrained environments and desktop setups alike. It focuses on correctness, low memory overhead, and simple outputs (CSV/JSON) so you can integrate it into embedded firmware, data pipelines, or mapping utilities.

Key use-cases:
- Collecting and logging coordinates on microcontrollers (UART/Serial).
- Translating NMEA sentences to structured formats for analytics.
- Computing speed, bearing, and simple filtering/validity checks in real time.

## ✨ Key Features

- NMEA parsing for common sentence types: GPRMC, GPGGA, GPGSV, GPGSA (extendable).
- Real-time serial stream processing with configurable sampling and buffering.
- Simple exporters: CSV, JSON; easy to adapt to other targets (MQTT, HTTP).
- Small footprint: suitable for microcontrollers (e.g., ESP32, STM32) or embedded Linux devices (Raspberry Pi).
- Optional smoothing and basic sanity checks (satellite fix, HDOP thresholds).
- Well-documented command-line interface and library hooks for embedding.

## 🛠️ Supported Platforms & Requirements

- Languages: Python 3.8+ (primary), optional C++ components for embedded ports (see /src or docs).
- Hardware: Any GPS module that emits NMEA sentences over UART/Serial (e.g., u-blox NEO-6M/8M).
- Typical Python dependencies:
  - pyserial
  - numpy (optional, for smoothing/metrics)
  - click or argparse (for the CLI)

Install Python dependencies:

```bash
python -m pip install -r requirements.txt
# or, if no requirements file:
python -m pip install pyserial
```

## 🚀 Quickstart (CLI)

1. Connect your GPS module to a serial port (e.g., /dev/ttyUSB0, COM3).
2. Run the tracker:

```bash
# Example: read from serial and write CSV
python -m tracker.cli --port /dev/ttyUSB0 --baud 9600 --output track.csv --format csv

# Example: stream parsed JSON to stdout
python -m tracker.cli --port /dev/ttyUSB0 --baud 9600 --format json
```

CLI flags (examples — match to actual implementation):
- --port: serial device (required)
- --baud: baud rate (default: 9600)
- --output: path to save CSV/JSON output (default: stdout)
- --format: csv|json
- --min-satellites: drop fixes with fewer than N satellites

## 📚 Library Usage (Python)

Import the parser and feed it raw NMEA lines:

```python
from tracker.parser import NMEAParser

parser = NMEAParser()
with open('nmea_sample.txt') as f:
    for line in f:
        record = parser.feed(line)
        if record and record.fix_ok:
            # record: object/dict with latitude, longitude, speed_knots, timestamp, satellites, hdop
            print(record.to_json())
```

Adjust for your repo's actual API names and classes.

## 🔧 Configuration & Tuning

- Sampling rate: control how many parsed messages are persisted vs. skipped.
- Filters: discard points with no fix, low satellite count, or very old timestamps.
- Output formatting: numeric precision, timezones (store in UTC by default).

## 🧪 Testing and Validation

- Add unit tests for the parser using recorded NMEA logs (place fixtures in tests/fixtures).
- Validate coordinate conversions and speed/bearing calculations against known-good examples.

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

---

Thank you for using Embedded-GPS-tracker — if you'd like, I can add example NMEA fixtures, a minimal Docker-based test runner, or a quick hardware wiring guide next.
