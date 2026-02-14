# src/askesigraph/rdf/query.py
from typing import List, Dict, Optional
from datetime import datetime
from pyoxigraph import Store
from askesigraph.rdf.graphs import GraphNames
from askesigraph.rdf.namespaces import Namespace

class MeasurementQuery:
    """High-level query interface over core ontology"""
    
    def __init__(self, store: Store):
        self.store = store
    
    def get_measurements(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        metrics: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Query core ontology for measurements.
        This queries ONLY the materialized core graph.
        """
        
        # Build dynamic SPARQL
        filters = []
        if start_date:
            filters.append(
                f'FILTER(?timestamp >= "{start_date.isoformat()}"^^xsd:dateTime)'
            )
        if end_date:
            filters.append(
                f'FILTER(?timestamp <= "{end_date.isoformat()}"^^xsd:dateTime)'
            )
        
        filter_clause = "\n    ".join(filters)
        
        # Optional metrics (if None, fetch all)
        optional_clauses = """
            OPTIONAL { ?measurement akg:weightKg ?weightKg }
            OPTIONAL { ?measurement akg:bodyFatPercentage ?bodyFat }
            OPTIONAL { ?measurement akg:muscleMassKg ?muscleMass }
            OPTIONAL { ?measurement akg:boneMassKg ?boneMass }
            OPTIONAL { ?measurement akg:bodyWaterPercentage ?bodyWater }
            OPTIONAL { ?measurement akg:basalMetabolicRate ?bmr }
            OPTIONAL { ?measurement akg:bmi ?bmi }
            OPTIONAL { ?measurement akg:metabolicAge ?metabolicAge }
        """
        
        query = f"""
        PREFIX akg: <{Namespace.AKG}>
        PREFIX xsd: <{Namespace.XSD}>
        
        SELECT ?measurement ?timestamp ?weightKg ?bodyFat ?muscleMass 
               ?boneMass ?bodyWater ?bmr ?bmi ?metabolicAge ?vendorSource
        FROM <{GraphNames.CORE}>
        WHERE {{
            ?measurement a akg:BodyMeasurement ;
                        akg:measuredAt ?timestamp .
            
            OPTIONAL {{ ?measurement akg:derivedFrom ?vendorSource }}
            
            {optional_clauses}
            
            {filter_clause}
        }}
        ORDER BY ?timestamp
        """
        
        results = []
        for solution in self.store.query(query):
            results.append({
                'measurement_id': str(solution['measurement']),
                'timestamp': solution['timestamp'].value,
                'weight_kg': float(solution['weightKg']) if solution.get('weightKg') else None,
                'body_fat_percentage': float(solution['bodyFat']) if solution.get('bodyFat') else None,
                'muscle_mass_kg': float(solution['muscleMass']) if solution.get('muscleMass') else None,
                'bone_mass_kg': float(solution['boneMass']) if solution.get('boneMass') else None,
                'body_water_percentage': float(solution['bodyWater']) if solution.get('bodyWater') else None,
                'bmr': int(solution['bmr']) if solution.get('bmr') else None,
                'bmi': float(solution['bmi']) if solution.get('bmi') else None,
                'metabolic_age': float(solution['metabolicAge']) if solution.get('metabolicAge') else None,
                'vendor_source': str(solution['vendorSource']) if solution.get('vendorSource') else None,
            })
        
        return results
    
    def get_vendor_measurement(self, measurement_id: str) -> Dict:
        """
        Trace back to original vendor data for provenance/debugging.
        This demonstrates cross-graph queries.
        """
        
        query = f"""
        PREFIX akg: <{Namespace.AKG}>
        PREFIX arboleaf: <{Namespace.ARBOLEAF}>
        
        SELECT ?vendorMeasurement ?measureTime ?weightLb ?deviceMac
        WHERE {{
            GRAPH <{GraphNames.CORE}> {{
                <{measurement_id}> akg:derivedFrom ?vendorMeasurement .
            }}
            
            GRAPH <{GraphNames.ARBOLEAF}> {{
                ?vendorMeasurement a arboleaf:Measurement ;
                                  arboleaf:measureTime ?measureTime ;
                                  arboleaf:weightLb ?weightLb .
                OPTIONAL {{ ?vendorMeasurement arboleaf:deviceMacAddress ?deviceMac }}
            }}
        }}
        """
        
        solution = next(self.store.query(query), None)
        if not solution:
            return {}
        
        return {
            'vendor_measurement': str(solution['vendorMeasurement']),
            'measure_time': str(solution['measureTime']),
            'weight_lb': float(solution['weightLb']),
            'device_mac': str(solution['deviceMac']) if solution.get('deviceMac') else None,
        }
