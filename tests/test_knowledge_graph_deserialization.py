from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from src.graph.knowledge_graph import KnowledgeGraph


class TestKnowledgeGraphDeserialization(unittest.TestCase):
    def _write_json(self, payload: dict) -> Path:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        path = Path(tmp.name)
        with tmp:
            tmp.write(json.dumps(payload))
        return path

    def test_load_from_raw_node_link_payload(self) -> None:
        graph = KnowledgeGraph()
        graph.add_module_node("src/a.py", language="python")
        graph.add_module_node("src/b.py", language="python")
        graph.add_import_edge("src/a.py", "src/b.py")

        payload = graph.to_json_dict()
        path = self._write_json(payload)

        loaded = KnowledgeGraph.load_from_json(path)

        self.assertEqual(2, loaded.module_graph.number_of_nodes())
        self.assertEqual(1, loaded.module_graph.number_of_edges())
        self.assertIn("src/a.py", loaded.node_objects)
        self.assertIn(("src/a.py", "src/b.py", "IMPORTS"), loaded.edge_objects)

    def test_load_from_wrapped_storage_payload(self) -> None:
        graph = KnowledgeGraph()
        graph.add_module_node("src/a.py", language="python")
        graph.add_module_node("src/b.py", language="python")
        graph.add_import_edge("src/a.py", "src/b.py")

        wrapped_payload = {
            "graph": graph.to_json_dict(),
            "sources": ["src/a.py"],
            "sinks": ["src/b.py"],
            "warnings": [],
        }
        path = self._write_json(wrapped_payload)

        loaded = KnowledgeGraph.load_from_json(path)

        self.assertEqual(2, loaded.module_graph.number_of_nodes())
        self.assertEqual(1, loaded.module_graph.number_of_edges())
        self.assertIn("src/b.py", loaded.node_objects)
        self.assertIn(("src/a.py", "src/b.py", "IMPORTS"), loaded.edge_objects)

    def test_from_json_dict_reconstructs_typed_graph_objects(self) -> None:
        payload = {
            "graph": {
                "directed": True,
                "multigraph": False,
                "graph": {},
                "nodes": [
                    {"id": "src/a.py", "node_type": "module", "path": "src/a.py", "language": "python"},
                    {"id": "src/b.py", "node_type": "module", "path": "src/b.py", "language": "python"},
                ],
                "links": [
                    {"source": "src/a.py", "target": "src/b.py", "edge_type": "IMPORTS", "weight": 2}
                ],
            },
            "sources": ["src/a.py"],
        }

        loaded = KnowledgeGraph.from_json_dict(payload)

        self.assertEqual(2, loaded.module_graph.number_of_nodes())
        self.assertEqual(1, loaded.module_graph.number_of_edges())
        self.assertEqual("module", loaded.module_graph.nodes["src/a.py"]["node_type"])
        self.assertEqual(2, loaded.module_graph.edges["src/a.py", "src/b.py"]["weight"])
        self.assertIn(("src/a.py", "src/b.py", "IMPORTS"), loaded.edge_objects)

    def test_add_node_rejects_untyped_payload(self) -> None:
        graph = KnowledgeGraph()
        with self.assertRaises(ValueError):
            graph.add_node("src/a.py", {"path": "src/a.py", "language": "python"})

    def test_add_edge_rejects_invalid_edge_type(self) -> None:
        graph = KnowledgeGraph()
        with self.assertRaises(ValidationError):
            graph.add_edge(
                {
                    "source": "src/a.py",
                    "target": "src/b.py",
                    "edge_type": "INVALID",
                }
            )


if __name__ == "__main__":
    unittest.main()
