import argparse
import sys
from pathlib import Path

from askesigraph.ingest import ArboleafIngest
from askesigraph.view import plot_body_metrics


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
        prog="akg",
        description="AskesiGraph Excel ingestion tool",
    )

    parser.add_argument(
        "excel",
        type=excel_file,
        help="Path to an Excel file",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    excel_path: Path = args.excel

    print(f"Using Excel file: {excel_path}")

    arboleaf_sheet = ArboleafIngest(excel_path).get_sheet()
    plot_body_metrics(arboleaf_sheet.rows, "/home/griff/git/AskesiGraph/data/test.png")


if __name__ == "__main__":
    main(sys.argv[1:])
