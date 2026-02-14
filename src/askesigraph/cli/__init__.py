"""
AskesiGraph CLI - Command-line interface for semantic health data integration.

This package provides subcommands for:
- ontology: Load and manage ontology definitions
- mappings: Load and manage ontology mappings
- ingest: Import vendor data into RDF graphs
- materialize: Transform vendor data to core ontology
- query: Query measurement data
- visualize: Generate charts and visualizations
- export: Export RDF graphs
- audit: Trace provenance of measurements
"""

import argparse
import sys
from pathlib import Path

from askesigraph.cli import ontology, mappings, ingest, materialize, query, visualize, export, audit


def excel_file(path: str) -> Path:
    """Validate Excel file path"""
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


def turtle_file(path: str) -> Path:
    """Validate Turtle/RDF file path"""
    p = Path(path)

    if not p.exists():
        raise argparse.ArgumentTypeError(f"File does not exist: {p}")

    if not p.is_file():
        raise argparse.ArgumentTypeError(f"Not a file: {p}")

    if p.suffix.lower() not in {".ttl", ".turtle", ".rdf", ".nt", ".nq"}:
        raise argparse.ArgumentTypeError(
            f"Expected an RDF file (.ttl, .rdf, .nt, .nq), got: {p.suffix}"
        )

    return p


def build_parser() -> argparse.ArgumentParser:
    """Build the main argument parser with all subcommands"""
    parser = argparse.ArgumentParser(
        prog="akg",
        description="AskesiGraph - Personal health data aggregation and semantic integration",
        epilog="For more information, see: https://github.com/yourusername/askesigraph",
    )

    # Global options
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("askesigraph.db"),
        help="Path to RDF database (default: askesigraph.db)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # Register all subcommands
    ontology.register_subcommand(subparsers)
    mappings.register_subcommand(subparsers)
    ingest.register_subcommand(subparsers)
    materialize.register_subcommand(subparsers)
    query.register_subcommand(subparsers)
    visualize.register_subcommand(subparsers)
    export.register_subcommand(subparsers)
    audit.register_subcommand(subparsers)

    return parser


def main(argv: list[str] | None = None) -> None:
    """Main entry point for the CLI"""
    parser = build_parser()
    args = parser.parse_args(argv)

    # Dispatch to appropriate command handler
    try:
        if args.command == "ontology":
            ontology.handle_command(args)
        elif args.command == "mappings":
            mappings.handle_command(args)
        elif args.command == "ingest":
            ingest.handle_command(args)
        elif args.command == "materialize":
            materialize.handle_command(args)
        elif args.command == "query":
            query.handle_command(args)
        elif args.command == "visualize":
            visualize.handle_command(args)
        elif args.command == "export":
            export.handle_command(args)
        elif args.command == "audit":
            audit.handle_command(args)
        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
