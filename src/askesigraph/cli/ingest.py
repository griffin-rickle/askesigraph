"""
Data ingestion commands.

Handles importing raw vendor data into vendor-specific RDF graphs.
No transformation is performed - data is stored in its original format.
"""

import argparse
import sys
import uuid
from pathlib import Path

from askesigraph.model.arboleaf import ArboleafIngest
from askesigraph.rdf.store import RDFStore
from askesigraph.rdf.ingest import VendorDataIngester


def register_subcommand(subparsers) -> None:
    """Register the ingest subcommand"""
    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Ingest data from various sources",
        description="Import raw vendor data into vendor-specific graphs",
    )
    ingest_parser.add_argument(
        "source",
        choices=["arboleaf", "withings", "garmin"],
        help="Data source type",
    )
    ingest_parser.add_argument(
        "file",
        type=Path,
        help="Path to data file",
    )
    ingest_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate without inserting into database",
    )


def handle_command(args: argparse.Namespace) -> None:
    """Handle ingest command"""
    if args.source == "arboleaf":
        ingest_arboleaf(args)
    elif args.source == "withings":
        print(f"Error: Source '{args.source}' not yet implemented")
        sys.exit(1)
    elif args.source == "garmin":
        print(f"Error: Source '{args.source}' not yet implemented")
        sys.exit(1)


def ingest_arboleaf(args: argparse.Namespace) -> None:
    """Ingest Arboleaf Excel data into vendor graph"""
    store = RDFStore(args.db)

    print(f"Ingesting Arboleaf data from {args.file}")

    # Parse Excel file
    sheet = ArboleafIngest(args.file).get_sheet()
    print(f"  Found {len(sheet.rows)} measurements")

    if args.dry_run:
        print("  [DRY RUN] Would insert into vendor graph")
        # Show sample
        if sheet.rows:
            print("\n  Sample (first row):")
            row = sheet.rows[0]
            print(f"    Time: {row.measure_time}")
            print(f"    Weight: {row.weight} lb")
            print(f"    Body Fat: {row.body_fat}%")
        return

    # Ingest into vendor graph
    ingester = VendorDataIngester()
    count = 0
    for row in sheet.rows:
        measurement_id = str(uuid.uuid4())
        quads = ingester.arboleaf_row_to_quads(row, measurement_id)
        for quad in quads:
            store.store.add(quad)
        count += 1

    print(f"✓ Ingested {count} measurements into Arboleaf vendor graph")
