"""
Audit commands.

Traces measurements back to their vendor sources for provenance analysis.
"""

import argparse

from askesigraph.rdf.store import RDFStore
from askesigraph.rdf.query import MeasurementQuery


def register_subcommand(subparsers) -> None:
    """Register the audit subcommand"""
    audit_parser = subparsers.add_parser(
        "audit",
        help="Audit and trace measurements",
        description="Trace measurements back to vendor sources for provenance",
    )
    audit_parser.add_argument(
        "measurement_id",
        type=str,
        help="Core measurement ID to audit",
    )


def handle_command(args: argparse.Namespace) -> None:
    """Handle audit command"""
    store = RDFStore(args.db)
    query_engine = MeasurementQuery(store.store)

    print(f"Auditing measurement: {args.measurement_id}\n")

    vendor_data = query_engine.get_vendor_measurement(args.measurement_id)

    if not vendor_data:
        print("✗ Measurement not found or no vendor source linked")
        return

    print("Provenance Trail:")
    print("-" * 60)
    print(f"Vendor Source:    {vendor_data.get('vendor_measurement', 'N/A')}")
    print(f"Original Time:    {vendor_data.get('measure_time', 'N/A')}")
    print(f"Original Weight:  {vendor_data.get('weight_lb', 'N/A')} lb")
    print(f"Device:           {vendor_data.get('device_mac', 'N/A')}")
