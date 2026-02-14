# src/askesigraph/rdf/ingest.py
from typing import Iterator
from pyoxigraph import Quad, NamedNode, Literal
from askesigraph.model.arboleaf import ArboleafRow
from askesigraph.rdf.graphs import GraphNames
from askesigraph.rdf.namespaces import Namespace

class VendorDataIngester:
    """Ingest raw vendor data into vendor-specific graphs"""
    
    @staticmethod
    def arboleaf_row_to_quads(row: ArboleafRow, measurement_id: str) -> Iterator[Quad]:
        """Convert Arboleaf row to vendor-ontology triples (NO translation)"""
        
        subject = NamedNode(f"{Namespace.VENDOR}arboleaf/{measurement_id}")
        graph = GraphNames.ARBOLEAF
        
        # Type
        yield Quad(
            subject,
            NamedNode(f"{Namespace.RDF}type"),
            NamedNode(f"{Namespace.ARBOLEAF}Measurement"),
            graph
        )
        
        # Temporal (preserve original format)
        yield Quad(
            subject,
            NamedNode(f"{Namespace.ARBOLEAF}measureTime"),
            Literal(row.measure_time.strftime("%m/%d/%Y %H:%M:%S")),
            graph
        )
        
        # Body metrics (preserve imperial units)
        yield Quad(
            subject,
            NamedNode(f"{Namespace.ARBOLEAF}weightLb"),
            Literal(str(row.weight), datatype=NamedNode(f"{Namespace.XSD}decimal")),
            graph
        )
        
        if row.body_fat is not None:
            yield Quad(
                subject,
                NamedNode(f"{Namespace.ARBOLEAF}bodyFatPercentage"),
                Literal(str(row.body_fat), datatype=NamedNode(f"{Namespace.XSD}decimal")),
                graph
            )
        
        if row.muscle_mass is not None:
            yield Quad(
                subject,
                NamedNode(f"{Namespace.ARBOLEAF}muscleMassLb"),
                Literal(str(row.muscle_mass), datatype=NamedNode(f"{Namespace.XSD}decimal")),
                graph
            )
        
        # ... all other fields in original format
        
        # Device info
        if row.device_mac_address:
            yield Quad(
                subject,
                NamedNode(f"{Namespace.ARBOLEAF}deviceMacAddress"),
                Literal(row.device_mac_address),
                graph
            )
