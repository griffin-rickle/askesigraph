"""
Export commands.

Exports RDF graphs in various serialization formats.
"""

import argparse
from pathlib import Path

from askesigraph.rdf.store import RDFStore
from askesigraph.rdf.graphs import GraphNames


def register_subcommand(subparsers) -> None:
    """Register the export subcommand"""
    export_parser = subparsers.add_parser(
        "export",
        help="Export data",
        description="Export RDF graphs in various formats",
    )
    export_parser.add_argument(
        "output",
        type=Path,
        help="Output file path",
    )
    export_parser.add_argument(
        "--graph",
        choices=["core", "vendor", "mappings", "all"],
        default="core",
        help="Which graph to export",
    )
    export_parser.add_argument(
        "--format",
        choices=["turtle", "ntriples", "rdfxml"],
        default="turtle",
        help="RDF serialization format",
    )


def handle_command(args: argparse.Namespace) -> None:
    """Handle export command"""
    store = RDFStore(args.db)

    # Determine which graph(s) to export
    if args.graph == "core":
        graphs = [GraphNames.CORE]
    elif args.graph == "vendor":
        graphs = [GraphNames.ARBOLEAF]  # Add others as implemented
    elif args.graph == "mappings":
        graphs = [GraphNames.MAPPINGS]
    elif args.graph == "all":
        graphs = None  # Export entire store

    # Map format names to MIME types
    format_map = {
        "turtle": "text/turtle",
        "ntriples": "application/n-triples",
        "rdfxml": "application/rdf+xml",
    }

    mime_type = format_map[args.format]

    print(f"Exporting {args.graph} graph(s) to {args.output} as {args.format}...")

    if graphs is None:
        # Export entire store
        store.export_store(args.output, mime_type)
    else:
        # Export specific graph(s)
        for graph in graphs:
            store.export_graph(args.output, graph, mime_type)

    print(f"✓ Exported to {args.output}")
