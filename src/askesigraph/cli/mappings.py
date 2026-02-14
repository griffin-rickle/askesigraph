"""
Mapping management commands.

Handles loading and listing ontology mapping definitions that describe
transformations between vendor-specific and core ontologies.
"""

import argparse
from pathlib import Path

from askesigraph.rdf.store import RDFStore
from askesigraph.rdf.graphs import GraphNames
from askesigraph.rdf.materialization import MaterializationEngine


def register_subcommand(subparsers) -> None:
    """Register the mappings subcommand and its sub-subcommands"""
    mappings_parser = subparsers.add_parser(
        "mappings",
        help="Manage ontology mappings",
        description="Load and query ontology mapping definitions",
    )
    mappings_subparsers = mappings_parser.add_subparsers(
        dest="mappings_command", 
        required=True
    )

    # mappings load
    mappings_load = mappings_subparsers.add_parser(
        "load",
        help="Load mapping definitions",
    )
    mappings_load.add_argument(
        "file",
        type=Path,
        help="Path to mappings file (.ttl)",
    )
    mappings_load.add_argument(
        "--source",
        type=str,
        required=True,
        help="Source vendor name (e.g., 'arboleaf')",
    )

    # mappings list
    mappings_list = mappings_subparsers.add_parser(
        "list",
        help="List all loaded mappings",
    )
    mappings_list.add_argument(
        "--source",
        type=str,
        help="Filter by source vendor",
    )


def handle_command(args: argparse.Namespace) -> None:
    """Handle mappings subcommand dispatch"""
    if args.mappings_command == "load":
        cmd_load(args)
    elif args.mappings_command == "list":
        cmd_list(args)


def cmd_load(args: argparse.Namespace) -> None:
    """Load mapping definitions"""
    store = RDFStore(args.db)

    print(f"Loading mappings for {args.source} from {args.file}")
    count = store.load_file(args.file, GraphNames.MAPPINGS)
    print(f"✓ Loaded {count} mapping triples")

    if args.verbose:
        # Query to show what mappings were loaded
        engine = MaterializationEngine(store.store)
        mappings = engine.load_mappings(args.source)
        print(f"\n  Found {len(mappings)} property mappings:")
        for m in mappings[:5]:  # Show first 5
            source_prop = m['source_property'].split('#')[-1]
            target_prop = m['target_property'].split('#')[-1]
            print(f"    {source_prop} → {target_prop}")
        if len(mappings) > 5:
            print(f"    ... and {len(mappings) - 5} more")


def cmd_list(args: argparse.Namespace) -> None:
    """List all loaded mappings"""
    store = RDFStore(args.db)
    engine = MaterializationEngine(store.store)

    # For now, hardcode known sources - could query this dynamically
    sources = ["arboleaf"] if not args.source else [args.source]

    print("\nLoaded Mappings:")
    print("-" * 80)

    for source in sources:
        try:
            mappings = engine.load_mappings(source)
            print(f"\n{source.upper()} → Core ({len(mappings)} mappings):")

            for m in mappings:
                source_prop = m['source_property'].split('#')[-1]
                target_prop = m['target_property'].split('#')[-1]
                transform = m['transform_type'].split('#')[-1]

                detail = ""
                if "Multiply" in transform and m.get('factor'):
                    detail = f" (×{m['factor']})"
                elif "DateTime" in transform and m.get('source_format'):
                    detail = f" ({m['source_format']})"

                print(f"  {source_prop:30s} → {target_prop:30s} [{transform}{detail}]")

        except Exception as e:
            print(f"  Error loading mappings for {source}: {e}")
