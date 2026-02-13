import csv
from datetime import datetime

from .model.myfitnesspal import MealEntry, MyFitnessPalData


# Parse CSV file
def load_myfitnesspal_csv(filepath: str) -> MyFitnessPalData:
    """Load and parse MyFitnessPal CSV export"""
    entries = []

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert empty strings to None for optional fields
            cleaned_row = {k: (None if v == "" else v) for k, v in row.items()}
            entries.append(MealEntry(**cleaned_row))

    return MyFitnessPalData(entries=entries)
