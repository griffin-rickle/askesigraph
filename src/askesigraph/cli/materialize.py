"""
Materialization commands.

Applies ontology mappings to transform vendor-specific data into the
core ontology representation. This is where the semantic integration happens.
"""

import argparse
import sys

from askesigraph.rdf.store import RDFStore
from askesigraph.rdf.graphs import GraphNames
from askesigraph.rdf.materialization import MaterializationEngine


def register_subcommand(subparsers) -> None:
    """Register the materialize subcommand"""
    materialize_parser = subparsers.add_parser(
        "materialize",
        help="Materialize core ontology from vendor data",
        description="Apply mappings to transform vendor data into core ontology",
    )
    materialize_parser.add_argument(
        "--source",
        type=str,
        required=True,
        choices=["arboleaf", "withings", "garmin", "all"],
        help="Source vendor to materialize from",
    )
    materialize_parser.add_argument(
        "--incremental",
        action="store_true",
        help="Only materialize new measurements (not yet in core graph)",
    )
    materialize_parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-materialization (clear existing core data first)",
    )


def handle_command(args: argparse.Namespace) -> None:
    """Handle materialize command"""
    store = RDFStore(args.db)
    engine = MaterializationEngine(store.store)

    if args.force and not args.incremental:
        print("⚠ Clearing existing core graph...")
        store.clear_graph(GraphNames.CORE)

    sources = ["arboleaf", "withings", "garmin"] if args.source == "all" else [args.source]

    total_count = 0
    for source in sources:
        print(f"\nMaterializing from {source}...")

        try:
            if source == "arboleaf":
                count = engine.materialize_from_arboleaf()
                print(f"✓ Materialized {count} measurements from {source}")
                total_count += count
            else:
                print(f"  Source '{source}' not yet implemented")

        except Exception as e:
            print(f"✗ Error materializing from {source}: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()

    print(f"\n✓ Total: {total_count} measurements materialized")
