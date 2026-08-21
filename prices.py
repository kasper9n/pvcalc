# prices.py
import csv
from datetime import datetime, timedelta
from pathlib import Path

import requests

from config import params

url = "https://www.hvakosterstrommen.no/api/v1/prices"
output_file = Path("output/pricestest.csv")

start_date = datetime.fromisoformat(params["start_time"]).date()
end_date = datetime.fromisoformat(params["end_time"]).date()

output_file.parent.mkdir(parents=True, exist_ok=True)

with output_file.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    _ = writer.writerow(["timestamp", "price_eur_kwh", "price_nok_kwh"])

    current_date = start_date

    while current_date <= end_date:
        date_string = current_date.strftime("%Y-%m-%d")

        print(f"Fetching {date_string}...", flush=True)

        response = requests.get(
            f"{url}/{current_date.year}/{current_date.month:02d}-{current_date.day:02d}_NO1.json",
            timeout=30,
        )
        response.raise_for_status()

        for row in response.json():
            _ = writer.writerow(
                [
                    row["time_start"],
                    row["EUR_per_kWh"],
                    row["NOK_per_kWh"],
                ]
            )

        current_date += timedelta(days=1)

print(f"Saved to {output_file}")
