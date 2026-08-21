import csv
from collections import defaultdict
from pathlib import Path

pvgis_file = Path("output/pvgis.csv")
prices_file = Path("output/prices.csv")
output_file = Path("output/earnings.csv")


def normalize_timestamp(timestamp):
    return timestamp[:19]


# Load electricity prices indexed by timestamp.
prices = {}

with prices_file.open("r", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        timestamp = normalize_timestamp(row["timestamp"])
        prices[timestamp] = row


monthly_totals = defaultdict(float)
yearly_totals = defaultdict(float)

total_earnings = 0.0
rows_written = 0

missing_pv = []
missing_prices = []


with (
    pvgis_file.open("r", newline="", encoding="utf-8") as pvgis_f,
    output_file.open("w", newline="", encoding="utf-8") as output_f,
):
    reader = csv.DictReader(pvgis_f)

    writer = csv.writer(output_f)

    writer.writerow(
        [
            "timestamp",
            "power_w",
            "energy_kwh",
            "price_eur_kwh",
            "price_nok_kwh",
            "earnings_nok",
        ]
    )

    for pv in reader:
        timestamp = normalize_timestamp(pv["timestamp"])

        # Handle missing PV value.
        if pv["power_w"].strip():
            power_w = float(pv["power_w"])
        else:
            power_w = 0.0
            missing_pv.append(timestamp)

        # Handle missing electricity price.
        price = prices.get(timestamp)

        if price is None:
            missing_prices.append(timestamp)
            continue

        price_eur_kwh = float(price["price_eur_kwh"])
        price_nok_kwh = float(price["price_nok_kwh"])

        energy_kwh = power_w / 1000
        earnings_nok = energy_kwh * price_nok_kwh

        total_earnings += earnings_nok

        year = timestamp[:4]
        month = timestamp[:7]

        yearly_totals[year] += earnings_nok
        monthly_totals[month] += earnings_nok

        writer.writerow(
            [
                timestamp,
                power_w,
                energy_kwh,
                price_eur_kwh,
                price_nok_kwh,
                earnings_nok,
            ]
        )

        rows_written += 1


print()
print(f"Saved to {output_file}")
print(f"Hourly rows: {rows_written}")

print()
print(f"Missing PV values: {len(missing_pv)}")

if missing_pv:
    for timestamp in missing_pv:
        print(f"  MISSING PV:    {timestamp}")

print()
print(f"Missing prices: {len(missing_prices)}")

if missing_prices:
    for timestamp in missing_prices:
        print(f"  MISSING PRICE: {timestamp}")

print()
print("Monthly earnings:")
for month, earnings in sorted(monthly_totals.items()):
    print(f"{month}: {earnings:,.2f} NOK")

print()
print("Yearly earnings:")
for year, earnings in sorted(yearly_totals.items()):
    print(f"{year}: {earnings:,.2f} NOK")

print()
print(f"TOTAL EARNINGS: {total_earnings:,.2f} NOK")
