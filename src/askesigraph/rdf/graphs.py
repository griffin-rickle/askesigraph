# src/askesigraph/rdf/graphs.py
from pyoxigraph import NamedNode

class GraphNames:
    """Named graph organization"""
    
    # Vendor data graphs (one per source)
    ARBOLEAF = NamedNode("http://askesigraph.com/graph/vendor/arboleaf")
    WITHINGS = NamedNode("http://askesigraph.com/graph/vendor/withings")
    GARMIN = NamedNode("http://askesigraph.com/graph/vendor/garmin")
    
    # Core ontology graph (materialized views)
    CORE = NamedNode("http://askesigraph.com/graph/core")
    
    # Ontology definitions
    ONTOLOGY_CORE = NamedNode("http://askesigraph.com/graph/ontology/core")
    ONTOLOGY_ARBOLEAF = NamedNode("http://askesigraph.com/graph/ontology/arboleaf")
    ONTOLOGY_MAPPING = NamedNode("http://askesigraph.com/graph/ontology/mapping")
    
    # Mapping instances
    MAPPINGS = NamedNode("http://askesigraph.com/graph/mappings")
