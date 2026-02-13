from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, Dict, List, Optional, Self, Tuple

import openpyxl
from openpyxl.cell import ReadOnlyCell
from pydantic.fields import Field
from pydantic.functional_validators import (
    BeforeValidator,
    ModelWrapValidatorHandler,
    model_validator,
)
from pydantic.main import BaseModel




# TODO: Create abstract ExcelIngest, ExcelSheet, and ExcelRow classes. The Arboleaf stuff can then subclass these.
def arboleaf_str_to_date(value: str) -> datetime:
    return datetime.strptime(value, "%m/%d/%Y %H:%M:%S")


def is_nonempty_row(
    row_def: Tuple[
        ReadOnlyCell,
        ReadOnlyCell,
        ReadOnlyCell,
        ReadOnlyCell,
        ReadOnlyCell,
        ReadOnlyCell,
        ReadOnlyCell,
        ReadOnlyCell,
        ReadOnlyCell,
        ReadOnlyCell,
        ReadOnlyCell,
        ReadOnlyCell,
        ReadOnlyCell,
        ReadOnlyCell,
        ReadOnlyCell,
        ReadOnlyCell,
        ReadOnlyCell,
        ReadOnlyCell,
        ReadOnlyCell,
    ],
) -> bool:
    return len(tuple(x for x in row_def if x.value is not None)) != 0


class ArboleafRow(BaseModel):
    measure_time: Annotated[datetime, BeforeValidator(arboleaf_str_to_date)] = Field(
        alias="Measure Time"
    )
    weight: float = Field(alias="Weight(lb)")
    body_fat: Optional[float] = Field(alias="Body Fat(%)")
    bmi: Optional[float] = Field(alias="BMI")
    skeletal_muscle: Optional[float] = Field(alias="Skeletal Muscle(%)")
    muscle_mass: Optional[float] = Field(alias="Muscle Mass(lb)")
    muscle_storage_ability: Optional[float] = Field(
        alias="Muscle Storage Ability Level"
    )
    protein: Optional[float] = Field(alias="Protein(%)")
    bmr: Optional[int] = Field(alias="BMR(kcal)")
    fat_free_body_weight: Optional[float] = Field(alias="Fat-free Body Weight(lb)")
    subcutaneous_fat: Optional[float] = Field(alias="Subcutaneous Fat Percentage(%)")
    visceral_fat: Optional[int] = Field(alias="Visceral Fat")
    body_water: Optional[float] = Field(alias="Body Water(%)")
    bone_mass: Optional[float] = Field(alias="Bone Mass(lb)")
    metabolic_age: Optional[float] = Field(alias="Metabolic Age")
    device_mac_address: Optional[str] = Field(alias="Device MAC Address")
    device_name: Optional[str] = Field(alias="Device Name")


class ArboleafSheet(BaseModel):
    header_row: int
    first_data_row: int
    sheet_name: str
    rows: List[ArboleafRow]

    @model_validator(mode="wrap")
    @classmethod
    def parse_rows(cls, data: Any, handler: ModelWrapValidatorHandler[Self]) -> Self:
        # TODO: Lazy load this stuff.
        all_rows = list(data["rows"])
        # -1 here because user puts 1, but arrays are zero-indexed here
        headers = tuple(header.value for header in all_rows[data["header_row"] - 1])
        data_rows = all_rows[data["first_data_row"] - 1 :]
        data["rows"] = [
            ArboleafRow(**dict(zip(headers, tuple(cell.value for cell in data_row))))
            for data_row in data_rows
        ]
        return handler(data)


class ArboleafIngest:
    def __init__(self, excel_path: Path):
        self.excel_path = excel_path

    def get_sheet(self, sheet_name: str = "Sheet1") -> ArboleafSheet:
        wb = openpyxl.load_workbook(self.excel_path, True)
        sheet = wb.get_sheet_by_name(sheet_name)
        test = ArboleafSheet(
            header_row=1, first_data_row=2, sheet_name=sheet_name, rows=sheet.rows
        )
        return test

