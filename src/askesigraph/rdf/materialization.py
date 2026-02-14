# src/askesigraph/rdf/materialization.py
from typing import Iterator, Dict, Any
from pyoxigraph import Store, Quad, NamedNode, Literal
from datetime import datetime
from askesigraph.rdf.graphs import GraphNames
from askesigraph.rdf.namespaces import Namespace

class MaterializationEngine:
    """
    Reads mapping triples and materializes core ontology from vendor data.
    This is the SPARQL engineering showcase.
    """
    
    def __init__(self, store: Store):
        self.store = store
    
    def load_mappings(self, vendor: str) -> list[Dict[str, Any]]:
        """Query mapping graph to get transformation rules"""
        
        query = f"""
        PREFIX map: <{Namespace.MAPPING}>
        PREFIX arboleaf: <{Namespace.ARBOLEAF}>
        PREFIX akg: <{Namespace.AKG}>
        PREFIX xsd: <{Namespace.XSD}>
        
        SELECT ?mapping ?sourceProperty ?targetProperty 
               ?transformType ?factor ?sourceFormat
        FROM <{GraphNames.MAPPINGS}>
        WHERE {{
            ?mapping a map:PropertyMapping ;
                     map:sourceProperty ?sourceProperty ;
                     map:targetProperty ?targetProperty ;
                     map:transformation ?transform .
            
            ?transform a ?transformType .
            
            OPTIONAL {{ ?transform map:factor ?factor }}
            OPTIONAL {{ ?transform map:sourceFormat ?sourceFormat }}
        }}
        """
        
        mappings = []
        for solution in self.store.query(query):
            mappings.append({
                'mapping': str(solution['mapping']),
                'source_property': str(solution['sourceProperty']),
                'target_property': str(solution['targetProperty']),
                'transform_type': str(solution['transformType']),
                'factor': float(solution['factor']) if solution.get('factor') else None,
                'source_format': str(solution['sourceFormat']) if solution.get('sourceFormat') else None,
            })
        
        return mappings
    
    def materialize_from_arboleaf(self) -> int:
        """
        Materialize core measurements from Arboleaf vendor data.
        Returns count of core measurements created.
        """
        
        mappings = self.load_mappings('arboleaf')
        
        # Group mappings by target (core measurement)
        # We need to process all properties for a given measurement together
        
        query = f"""
        PREFIX arboleaf: <{Namespace.ARBOLEAF}>
        PREFIX xsd: <{Namespace.XSD}>
        
        SELECT ?measurement ?measureTime ?weightLb ?bodyFat ?muscleMassLb 
               ?boneMassLb ?bodyWater ?bmr ?bmi ?metabolicAge ?deviceMac
        FROM <{GraphNames.ARBOLEAF}>
        WHERE {{
            ?measurement a arboleaf:Measurement ;
                        arboleaf:measureTime ?measureTime ;
                        arboleaf:weightLb ?weightLb .
            
            OPTIONAL {{ ?measurement arboleaf:bodyFatPercentage ?bodyFat }}
            OPTIONAL {{ ?measurement arboleaf:muscleMassLb ?muscleMassLb }}
            OPTIONAL {{ ?measurement arboleaf:boneMassLb ?boneMassLb }}
            OPTIONAL {{ ?measurement arboleaf:bodyWaterPercentage ?bodyWater }}
            OPTIONAL {{ ?measurement arboleaf:bmrKcal ?bmr }}
            OPTIONAL {{ ?measurement arboleaf:bmi ?bmi }}
            OPTIONAL {{ ?measurement arboleaf:metabolicAge ?metabolicAge }}
            OPTIONAL {{ ?measurement arboleaf:deviceMacAddress ?deviceMac }}
        }}
        ORDER BY ?measureTime
        """
        
        count = 0
        for solution in self.store.query(query):
            core_quads = self._materialize_measurement(solution, mappings)
            for quad in core_quads:
                self.store.add(quad)
            count += 1
        
        return count
    
    def _materialize_measurement(
        self, 
        vendor_data: Dict, 
        mappings: list[Dict[str, Any]]
    ) -> Iterator[Quad]:
        """Apply mappings to create core ontology triples"""
        
        # Generate core measurement IRI
        vendor_measurement = str(vendor_data['measurement'])
        core_measurement_id = vendor_measurement.split('/')[-1]  # Extract ID
        core_subject = NamedNode(f"{Namespace.MEASUREMENT}{core_measurement_id}")
        
        graph = GraphNames.CORE
        
        # Type
        yield Quad(
            core_subject,
            NamedNode(f"{Namespace.RDF}type"),
            NamedNode(f"{Namespace.AKG}BodyMeasurement"),
            graph
        )
        
        # Provenance link
        yield Quad(
            core_subject,
            NamedNode(f"{Namespace.AKG}derivedFrom"),
            NamedNode(vendor_measurement),
            graph
        )
        
        # Apply each mapping
        for mapping in mappings:
            source_prop = mapping['source_property'].split('#')[-1]
            target_prop = mapping['target_property']
            transform_type = mapping['transform_type']
            
            # Get source value
            # Map property name to solution key (arboleaf:weightLb → weightLb)
            source_key = self._property_to_key(source_prop)
            source_value = vendor_data.get(source_key)
            
            if source_value is None:
                continue
            
            # Apply transformation
            target_value = self._apply_transformation(
                source_value,
                transform_type,
                mapping
            )
            
            if target_value is not None:
                yield Quad(
                    core_subject,
                    NamedNode(target_prop),
                    target_value,
                    graph
                )
    
    def _apply_transformation(
        self,
        source_value: Any,
        transform_type: str,
        mapping: Dict[str, Any]
    ) -> Literal:
        """Apply transformation function to value"""
        
        if 'MultiplyTransform' in transform_type:
            # Numeric conversion (e.g., lb → kg)
            factor = mapping['factor']
            result = float(source_value) * factor
            return Literal(
                str(result),
                datatype=NamedNode(f"{Namespace.XSD}decimal")
            )
        
        elif 'DateTimeTransform' in transform_type:
            # Parse datetime string and convert to xsd:dateTime
            source_format = mapping['source_format']
            dt = datetime.strptime(str(source_value), source_format)
            return Literal(
                dt.isoformat(),
                datatype=NamedNode(f"{Namespace.XSD}dateTime")
            )
        
        elif 'DirectMapping' in transform_type:
            # 1:1 mapping
            if isinstance(source_value, (int, float)):
                datatype = NamedNode(f"{Namespace.XSD}decimal")
                return Literal(str(source_value), datatype=datatype)
            else:
                return Literal(str(source_value))
        
        return None
    
    def _property_to_key(self, property_name: str) -> str:
        """Convert RDF property name to query result key"""
        # arboleaf:weightLb → weightLb
        # This mapping depends on how you name SPARQL variables
        return property_name.replace('arboleaf:', '')
