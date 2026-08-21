AI slop Python project for calculating solar panel production and Norwegian electricity prices, every hour of the selected year. 

### pvgis.py

Generates `output/pvgis.csv` with electricity generation values. First time you run it, it creates a config.py file, which you can edit.
```
poetry run python pvgis.py
```

### prices.py

Generates `output/prices.csv` with Norwegian electricity prices.
```
poetry run python prices.py
```
