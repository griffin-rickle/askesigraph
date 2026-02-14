"""
Query commands.

Queries the materialized core ontology for measurement data.
Supports filtering by date range and output in various formats.
"""

import argparse
from datetime import datetime

from askesigraph.rdf.store import RDFStore
from askesigraph.rdf.query import MeasurementQuery


def register_subcommand(subparsers) -> None:
    """Register the query subcommand"""
    query_parser = subparsers.add_parser(
        "query",
        help="Query measurements",
        description="Query core ontology for measurements",
    )
    query_parser.add_argument(
        "--start",
        type=str,
        help="Start date (ISO format: YYYY-MM-DD)",
    )
    query_parser.add_argument(
        "--end",
        type=str,
        help="End date (ISO format: YYYY-MM-DD)",
    )
    query_parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format",
    )
    query_parser.add_argument(
        "--metrics",
        nargs="+",
        help="Specific metrics to query (e.g., weight body_fat)",
    )


def handle_command(args: argparse.Namespace) -> None:
    """Handle query command"""
    store = RDFStore(args.db)
    query_engine = MeasurementQuery(store.store)

    # Parse dates
    start_date = datetime.fromisoformat(args.start) if args.start else None
    end_date = datetime.fromisoformat(args.end) if args.end else None

    print("Querying measurements...")
    if start_date:
        print(f"  Start: {start_date.date()}")
    if end_date:
        print(f"  End: {end_date.date()}")

    results = query_engine.get_measurements(start_date, end_date, args.metrics)

    if args.format == "table":
        format_table(results)
    elif args.format == "json":
        format_json(results)
    elif args.format == "csv":
        format_csv(results)


def format_table(results: list) -> None:
    """Format results as a table"""
    print(f"\nFound {len(results)} measurements:\n")
    print(f"{'Timestamp':<20} {'Weight (kg)':<12} {'Body Fat %':<12} {'BMI':<8}")
    print("-" * 60)
    
    for r in results:
        timestamp = r['timestamp'].strftime('%Y-%m-%d %H:%M') if hasattr(r['timestamp'], 'strftime') else str(r['timestamp'])
        weight = f"{r['weight_kg']:.2f}" if r['weight_kg'] else "N/A"
        body_fat = f"{r['body_fat_percentage']:.1f}" if r['body_fat_percentage'] else "N/A"
        bmi = f"{r['bmi']:.1f}" if r['bmi'] else "N/A"
        print(f"{timestamp:<20} {weight:<12} {body_fat:<12} {bmi:<8}")


def format_json(results: list) -> None:
    """Format results as JSON"""
    import json
    
    # Convert datetime objects to strings for JSON serialization
    for r in results:
        if hasattr(r['timestamp'], 'isoformat'):
            r['timestamp'] = r['timestamp'].isoformat()
    
    print(json.dumps(results, indent=2))


def format_csv(results: list) -> None:
    """Format results as CSV"""
    import csv
    import sys
    
    if results:
        writer = csv.DictWriter(sys.stdout, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
