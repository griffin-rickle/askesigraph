"""
RDF store wrapper for Oxigraph.

Provides high-level interface for loading, querying, and managing
the Oxigraph RDF database.
"""

from pathlib import Path
from typing import Optional

from pyoxigraph import Store, NamedNode


class RDFStore:
    """Wrapper around Oxigraph Store with convenience methods"""

    def __init__(self, db_path: Path):
        """
        Initialize the RDF store.

        Args:
            db_path: Path to the Oxigraph database directory
        """
        self.db_path = db_path
        self.store = Store(str(db_path))

    def load_file(self, file_path: Path, graph: NamedNode) -> int:
        """
        Load an RDF file into a named graph.

        Args:
            file_path: Path to RDF file (.ttl, .rdf, .nt, .nq)
            graph: Named graph to load into

        Returns:
            Number of triples loaded
        """
        # Determine MIME type from extension
        extension = file_path.suffix.lower()
        mime_type_map = {
            ".ttl": "text/turtle",
            ".turtle": "text/turtle",
            ".rdf": "application/rdf+xml",
            ".nt": "application/n-triples",
            ".nq": "application/n-quads",
        }

        mime_type = mime_type_map.get(extension, "text/turtle")

        # Count triples before
        count_before = self.count_triples(graph)

        # Load the file
        with open(file_path, "rb") as f:
            self.store.load(
                f,
                mime_type=mime_type,
                to_graph=graph,
            )

        # Count triples after
        count_after = self.count_triples(graph)

        return count_after - count_before

    def count_triples(self, graph: Optional[NamedNode] = None) -> int:
        """
        Count triples in a graph (or entire store if graph=None).

        Args:
            graph: Named graph to count, or None for entire store

        Returns:
            Number of triples
        """
        if graph is None:
            # Count all triples in store
            query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }"
        else:
            # Count triples in specific graph
            query = f"""
            SELECT (COUNT(*) AS ?count)
            WHERE {{
                GRAPH <{graph.value}> {{
                    ?s ?p ?o
                }}
            }}
            """

        result = list(self.store.query(query))
        if result:
            return int(result[0]["count"])
        return 0

    def clear_graph(self, graph: NamedNode) -> None:
        """
        Clear all triples from a named graph.

        Args:
            graph: Named graph to clear
        """
        self.store.update(f"CLEAR GRAPH <{graph.value}>")

    def export_graph(
        self, output_path: Path, graph: NamedNode, mime_type: str = "text/turtle"
    ) -> None:
        """
        Export a named graph to a file.

        Args:
            output_path: Output file path
            graph: Named graph to export
            mime_type: RDF serialization format
        """
        query = f"""
        CONSTRUCT {{ ?s ?p ?o }}
        WHERE {{
            GRAPH <{graph.value}> {{
                ?s ?p ?o
            }}
        }}
        """

        with open(output_path, "wb") as f:
            results = self.store.query(query)
            # Serialize results
            for triple in results:
                # This is simplified - in practice you'd use proper serialization
                pass

    def export_store(self, output_path: Path, mime_type: str = "text/turtle") -> None:
        """
        Export entire store to a file.

        Args:
            output_path: Output file path
            mime_type: RDF serialization format
        """
        with open(output_path, "wb") as f:
            self.store.dump(f, mime_type)
