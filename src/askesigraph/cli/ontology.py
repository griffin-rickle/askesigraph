"""
Ontology management commands.

Handles loading and listing ontology definitions (core, vendor, mapping).
"""

import argparse
import sys
from pathlib import Path

from askesigraph.rdf.store import RDFStore
from askesigraph.rdf.graphs import GraphNames


def register_subcommand(subparsers) -> None:
    """Register the ontology subcommand and its sub-subcommands"""
    ontology_parser = subparsers.add_parser(
        "ontology",
        help="Manage ontologies",
        description="Load and manage ontology definitions",
    )
    ontology_subparsers = ontology_parser.add_subparsers(
        dest="ontology_command", 
        required=True
    )

    # ontology load
    ontology_load = ontology_subparsers.add_parser(
        "load",
        help="Load an ontology into the RDF store",
    )
    ontology_load.add_argument(
        "file",
        type=Path,
        help="Path to ontology file (.ttl, .rdf, .nt)",
    )
    ontology_load.add_argument(
        "--type",
        choices=["core", "vendor", "mapping"],
        required=True,
        help="Type of ontology being loaded",
    )
    ontology_load.add_argument(
        "--vendor-name",
        type=str,
        help="Vendor name (required when --type=vendor)",
    )

    # ontology list
    ontology_list = ontology_subparsers.add_parser(
        "list",
        help="List loaded ontologies",
    )


def handle_command(args: argparse.Namespace) -> None:
    """Handle ontology subcommand dispatch"""
    if args.ontology_command == "load":
        cmd_load(args)
    elif args.ontology_command == "list":
        cmd_list(args)


def cmd_load(args: argparse.Namespace) -> None:
    """Load an ontology file into the appropriate graph"""
    store = RDFStore(args.db)

    # Determine target graph
    if args.type == "core":
        graph = GraphNames.ONTOLOGY_CORE
        print(f"Loading core ontology from {args.file}")
    elif args.type == "vendor":
        if not args.vendor_name:
            print("Error: --vendor-name required when loading vendor ontology")
            sys.exit(1)
        graph = getattr(GraphNames, f"ONTOLOGY_{args.vendor_name.upper()}", None)
        if not graph:
            print(f"Error: Unknown vendor '{args.vendor_name}'")
            sys.exit(1)
        print(f"Loading {args.vendor_name} vendor ontology from {args.file}")
    elif args.type == "mapping":
        graph = GraphNames.ONTOLOGY_MAPPING
        print(f"Loading mapping ontology from {args.file}")

    # Load the file
    count = store.load_file(args.file, graph)
    print(f"✓ Loaded {count} triples into {args.type} ontology graph")

    if args.verbose:
        print(f"  Graph: {graph}")


def cmd_list(args: argparse.Namespace) -> None:
    """List loaded ontologies"""
    store = RDFStore(args.db)

    ontology_graphs = [
        ("Core", GraphNames.ONTOLOGY_CORE),
        ("Arboleaf Vendor", GraphNames.ONTOLOGY_ARBOLEAF),
        ("Mapping", GraphNames.ONTOLOGY_MAPPING),
    ]

    print("\nLoaded Ontologies:")
    print("-" * 60)

    for name, graph in ontology_graphs:
        count = store.count_triples(graph)
        status = "✓" if count > 0 else "✗"
        print(f"{status} {name:20s} {count:8d} triples")
