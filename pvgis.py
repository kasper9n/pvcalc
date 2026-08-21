import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path
from pprint import pformat
from zoneinfo import ZoneInfo

import requests

url = "https://photovoltaic-geographic-information-system.ec.europa.eu/api/v6/power/broadband"
config_file = Path("config.py")
output_file = Path("output/pvgis.csv")

default_params = {
    "latitude": 61.8,
    "longitude": 12.0,
    # Roof
    "surface_orientation": 180,
    "surface_tilt": 30,
    # Full year 2024
    "start_time": "2024-01-01T00:00:00",
    "end_time": "2024-12-31T23:59:59",
    "frequency": "Hourly",
    "timezone": "Europe/Oslo",
    # Solar data
    "irradiance_source": "SARAH-3",
    # PV system
    "photovoltaic_module": "cSi:Free standing 2025",
    "photovoltaic_module_type": "Mono-Facial",
    "system_efficiency": 0.86,
    "power_model": "Huld 2011",
    "peak-power": 1,
    # Analysis
    "horizon_profile": "PVGIS",
    "shading_model": "PVGIS",
}


if not config_file.exists():
    config_file.write_text(
        f"params = {pformat(default_params, sort_dicts=False)}\n",
        encoding="utf-8",
    )


from config import params

print("Fetching PVGIS v6...", flush=True)

response = requests.get(
    url,
    params=params,
    timeout=300,
)

print("HTTP:", response.status_code, flush=True)

response.raise_for_status()

data = response.json()
power = data["power"]

print(f"Received {len(power)} hourly values.", flush=True)

# Generate timestamps as real hourly instants in UTC,
# then convert them to Europe/Oslo for output.
oslo = ZoneInfo("Europe/Oslo")

start_local = datetime.fromisoformat(params["start_time"]).replace(tzinfo=oslo)

start_utc = start_local.astimezone(timezone.utc)

timestamps = [
    (start_utc + timedelta(hours=i)).astimezone(oslo) for i in range(len(power))
]

output_file.parent.mkdir(parents=True, exist_ok=True)

with output_file.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow(["timestamp", "power_w"])

    for timestamp, value in zip(timestamps, power):
        writer.writerow(
            [
                timestamp.isoformat(),
                value,
            ]
        )

print(f"Saved to {output_file}")
