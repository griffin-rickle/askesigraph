from datetime import date as Date
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class MealEntry(BaseModel):
    """Single meal entry from MyFitnessPal export"""

    date: Date = Field(alias="Date")
    meal: str = Field(alias="Meal")
    calories: Optional[float] = Field(alias="Calories")
    fat_g: Optional[float] = Field(alias="Fat (g)")
    saturated_fat: Optional[float] = Field(alias="Saturated Fat")
    polyunsaturated_fat: Optional[float] = Field(alias="Polyunsaturated Fat")
    monounsaturated_fat: Optional[float] = Field(alias="Monounsaturated Fat")
    trans_fat: Optional[float] = Field(alias="Trans Fat")
    cholesterol: Optional[float] = Field(alias="Cholesterol")
    sodium_mg: Optional[float] = Field(alias="Sodium (mg)")
    potassium: Optional[float] = Field(alias="Potassium")
    carbohydrates_g: Optional[float] = Field(alias="Carbohydrates (g)")
    fiber: Optional[float] = Field(alias="Fiber")
    sugar: Optional[float] = Field(alias="Sugar")
    protein_g: Optional[float] = Field(alias="Protein (g)")
    vitamin_a: Optional[float] = Field(alias="Vitamin A")
    vitamin_c: Optional[float] = Field(alias="Vitamin C")
    calcium: Optional[float] = Field(alias="Calcium")
    iron: Optional[float] = Field(alias="Iron")
    note: Optional[str] = Field(default=None, alias="Note")

    class Config:
        populate_by_name = True  # Allows using both alias and field name

    @field_validator("note", mode="before")
    @classmethod
    def empty_string_to_none(cls, v: str) -> Optional[str]:
        """Convert empty strings to None"""
        if v == "" or (isinstance(v, str) and v.strip() == ""):
            return None
        return v


class MyFitnessPalData(BaseModel):
    """Collection of meal entries"""

    entries: list[MealEntry]

    @property
    def total_calories(self) -> float:
        """Sum of all calories"""
        return sum(e.calories or 0 for e in self.entries)

    @property
    def total_protein(self) -> float:
        """Sum of all protein"""
        return sum(e.protein_g or 0 for e in self.entries)

    def by_date(self, target_date: Date) -> list[MealEntry]:
        """Get all entries for a specific date"""
        return [e for e in self.entries if e.date == target_date]

    def by_meal(self, meal_name: str) -> list[MealEntry]:
        """Get all entries for a specific meal type"""
        return [e for e in self.entries if e.meal.lower() == meal_name.lower()]
