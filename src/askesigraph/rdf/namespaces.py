# src/askesigraph/rdf/namespaces.py
"""
RDF namespace definitions for AskesiGraph.
Centralizes all IRI prefixes used throughout the system.
"""

class Namespace:
    """Core namespace definitions"""
    
    # Core ontology
    AKG = "http://askesigraph.com/ontology#"
    
    # Vendor ontologies
    ARBOLEAF = "http://askesigraph.com/vendor/arboleaf#"
    WITHINGS = "http://askesigraph.com/vendor/withings#"
    GARMIN = "http://askesigraph.com/vendor/garmin#"
    
    # Mapping ontology
    MAPPING = "http://askesigraph.com/mapping#"
    
    # Instance data namespaces
    MEASUREMENT = "http://askesigraph.com/measurement/"
    VENDOR = "http://askesigraph.com/vendor/"
    
    # Standard vocabularies
    RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    RDFS = "http://www.w3.org/2000/01/rdf-schema#"
    OWL = "http://www.w3.org/2002/07/owl#"
    XSD = "http://www.w3.org/2001/XMLSchema#"
    
    # Provenance (W3C PROV-O)
    PROV = "http://www.w3.org/ns/prov#"
    
    # Units (QUDT - Quantities, Units, Dimensions and Types)
    QUDT = "http://qudt.org/schema/qudt/"
    UNIT = "http://qudt.org/vocab/unit/"
    
    # Time ontology (for temporal reasoning if needed)
    TIME = "http://www.w3.org/2006/time#"
    
    # Dublin Core (for metadata)
    DC = "http://purl.org/dc/terms/"


class PrefixMap:
    """
    Prefix map for SPARQL queries and Turtle serialization.
    Useful for generating PREFIX declarations programmatically.
    """
    
    STANDARD = {
        'akg': Namespace.AKG,
        'arboleaf': Namespace.ARBOLEAF,
        'withings': Namespace.WITHINGS,
        'garmin': Namespace.GARMIN,
        'map': Namespace.MAPPING,
        'rdf': Namespace.RDF,
        'rdfs': Namespace.RDFS,
        'owl': Namespace.OWL,
        'xsd': Namespace.XSD,
        'prov': Namespace.PROV,
        'qudt': Namespace.QUDT,
        'unit': Namespace.UNIT,
        'time': Namespace.TIME,
        'dc': Namespace.DC,
    }
    
    @classmethod
    def to_sparql_prefixes(cls) -> str:
        """Generate SPARQL PREFIX declarations"""
        return '\n'.join(
            f"PREFIX {prefix}: <{uri}>"
            for prefix, uri in cls.STANDARD.items()
        )
    
    @classmethod
    def to_turtle_prefixes(cls) -> str:
        """Generate Turtle @prefix declarations"""
        return '\n'.join(
            f"@prefix {prefix}: <{uri}> ."
            for prefix, uri in cls.STANDARD.items()
        )


# Convenience functions for building IRIs

def measurement_iri(measurement_id: str) -> str:
    """Generate IRI for a core measurement"""
    return f"{Namespace.MEASUREMENT}{measurement_id}"


def vendor_measurement_iri(vendor: str, measurement_id: str) -> str:
    """Generate IRI for a vendor measurement"""
    return f"{Namespace.VENDOR}{vendor}/{measurement_id}"


def property_iri(namespace: str, property_name: str) -> str:
    """Generate IRI for a property"""
    return f"{namespace}{property_name}"


# Example usage in other modules:
# from askesigraph.rdf.namespaces import Namespace, PrefixMap
#
# query = f"""
# {PrefixMap.to_sparql_prefixes()}
# 
# SELECT ?measurement ?timestamp
# WHERE {{
#     ?measurement a akg:BodyMeasurement ;
#                 akg:measuredAt ?timestamp .
# }}
# """
