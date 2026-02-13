import argparse
import sys
from pathlib import Path

from askesigraph.ingest import load_myfitnesspal_csv
from askesigraph.model.arboleaf import ArboleafIngest
from askesigraph.view import plot_weight_and_calories


def excel_file(path: str) -> Path:
    p = Path(path)

    if not p.exists():
        raise argparse.ArgumentTypeError(f"File does not exist: {p}")

    if not p.is_file():
        raise argparse.ArgumentTypeError(f"Not a file: {p}")

    if p.suffix.lower() not in {".xlsx", ".xlsm", ".xltx", ".xltm"}:
        raise argparse.ArgumentTypeError(
            f"Expected an Excel file (.xlsx, .xlsm, .xltx, .xltm), got: {p.suffix}"
        )

    return p


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plot body metrics from Arboleaf and MyFitnessPal data"
    )
    parser.add_argument("excel", type=Path, help="Path to Arboleaf Excel file")
    parser.add_argument(
        "myfitnesspal", type=Path, help="Path to MyFitnessPal CSV export"
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    excel_path: Path = args.excel
    mfp_csv_path: Path = args.myfitnesspal  # Add this argument to your parser

    print(f"Using Excel file: {excel_path}")
    print(f"Using MyFitnessPal CSV: {mfp_csv_path}")

    # Load Arboleaf data
    arboleaf_sheet = ArboleafIngest(excel_path).get_sheet()

    # Load MyFitnessPal data
    mfp_data = load_myfitnesspal_csv(str(mfp_csv_path))

    from datetime import date

    start_date = date(2023, 10, 1)  # Change this to your desired start date

    # Create the plot
    plot_weight_and_calories(
        arboleaf_sheet.rows,
        mfp_data,
        "/home/griff/git/askesigraph/data/weight_calories.png",
        start_date=start_date,
    )


if __name__ == "__main__":
    main(sys.argv[1:])
