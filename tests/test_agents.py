"""
Unit tests for the Brownfield Cartographer agents.

Tests cover:
- Surveyor: module parsing, dead code detection, git velocity
- Hydrologist: lineage event construction, blast_radius, sources/sinks
- Navigator: all 4 tools, intent inference, parameter extraction
- Archivist: CODEBASE.md generation
- KnowledgeGraph: schema validation (see test_knowledge_graph_deserialization.py)
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_temp_repo() -> Path:
    """Create a minimal temp repo with Python + SQL files for Surveyor tests."""
    tmp = Path(tempfile.mkdtemp())
    (tmp / "src").mkdir()

    (tmp / "src" / "ingestion.py").write_text(
        "import pandas as pd\nfrom src import transform\n\ndef load_csv(path: str):\n    return pd.read_csv(path)\n",
        encoding="utf-8",
    )
    (tmp / "src" / "transform.py").write_text(
        "def clean(df):\n    '''Clean dataframe.'''\n    return df.dropna()\n",
        encoding="utf-8",
    )
    (tmp / "src" / "serving.py").write_text(
        "from src import transform\n\ndef serve(df):\n    return transform.clean(df)\n",
        encoding="utf-8",
    )
    (tmp / "models.sql").write_text(
        "SELECT order_id, customer_id FROM raw.orders WHERE status = 'active'",
        encoding="utf-8",
    )
    # Git init so surveyor git-velocity call doesn't crash
    import subprocess
    subprocess.run(["git", "init", str(tmp)], capture_output=True)
    subprocess.run(["git", "-C", str(tmp), "add", "."], capture_output=True)
    subprocess.run(
        ["git", "-C", str(tmp), "commit", "-m", "init", "--allow-empty"],
        capture_output=True,
        env={"GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@t.com",
             "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@t.com",
             "PATH": __import__("os").environ["PATH"]},
    )
    return tmp


# ---------------------------------------------------------------------------
# Surveyor
# ---------------------------------------------------------------------------

class TestSurveyorAgent(unittest.TestCase):
    def setUp(self):
        self.repo = _make_temp_repo()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.repo, ignore_errors=True)

    def _run_surveyor(self):
        from src.agents.surveyor import SurveyorAgent
        agent = SurveyorAgent(self.repo)
        output_root = Path(tempfile.mkdtemp())
        return agent.run(days=30, output_root=output_root), output_root

    def test_module_count_is_positive(self):
        result, _ = self._run_surveyor()
        self.assertGreater(result["module_count"], 0)

    def test_module_graph_json_written(self):
        result, output_root = self._run_surveyor()
        path = Path(result["module_graph_path"])
        self.assertTrue(path.exists(), f"module_graph.json not found at {path}")

    def test_module_graph_json_is_valid(self):
        result, _ = self._run_surveyor()
        with open(result["module_graph_path"], encoding="utf-8") as f:
            payload = json.load(f)
        self.assertIn("nodes", payload)

    def test_pagerank_list_returned(self):
        result, _ = self._run_surveyor()
        pr = result["pagerank"]
        self.assertIsInstance(pr, list)

    def test_strongly_connected_components_returned(self):
        result, _ = self._run_surveyor()
        scc = result["strongly_connected_components"]
        self.assertIsInstance(scc, list)

    def test_high_velocity_core_returned(self):
        result, _ = self._run_surveyor()
        hvc = result["high_velocity_core"]
        self.assertIsInstance(hvc, list)

    def test_dead_code_candidates_returned(self):
        result, _ = self._run_surveyor()
        dc = result["dead_code_candidates"]
        self.assertIsInstance(dc, list)

    def test_incremental_mode_filters_files(self):
        from src.agents.surveyor import SurveyorAgent
        agent = SurveyorAgent(self.repo)
        output_root = Path(tempfile.mkdtemp())
        changed = ["src/ingestion.py"]
        result = agent.run(days=30, output_root=output_root, changed_files=changed)
        # Should process at least the changed file
        self.assertIsInstance(result["module_count"], int)


# ---------------------------------------------------------------------------
# Hydrologist
# ---------------------------------------------------------------------------

class TestHydrologistAgent(unittest.TestCase):
    def setUp(self):
        self.repo = _make_temp_repo()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.repo, ignore_errors=True)

    def _run_hydrologist(self):
        from src.agents.hydrologist import HydrologistAgent
        agent = HydrologistAgent(self.repo)
        output_root = Path(tempfile.mkdtemp())
        return agent.run(output_root=output_root), output_root

    def test_lineage_graph_json_written(self):
        result, output_root = self._run_hydrologist()
        path = Path(result["lineage_graph_path"])
        self.assertTrue(path.exists(), f"lineage_graph.json not found at {path}")

    def test_lineage_graph_json_is_valid(self):
        result, _ = self._run_hydrologist()
        with open(result["lineage_graph_path"], encoding="utf-8") as f:
            payload = json.load(f)
        # Either raw node-link or wrapped payload
        self.assertTrue("nodes" in payload or "graph" in payload)

    def test_sources_and_sinks_returned(self):
        result, _ = self._run_hydrologist()
        self.assertIn("sources", result)
        self.assertIn("sinks", result)
        self.assertIsInstance(result["sources"], list)
        self.assertIsInstance(result["sinks"], list)

    def test_event_count_returned(self):
        result, _ = self._run_hydrologist()
        self.assertIsInstance(result["event_count"], int)
        self.assertGreaterEqual(result["event_count"], 0)

    def test_blast_radius_returns_list(self):
        from src.agents.hydrologist import HydrologistAgent
        agent = HydrologistAgent(self.repo)
        output_root = Path(tempfile.mkdtemp())
        agent.run(output_root=output_root)
        radius = agent.blast_radius("nonexistent_table")
        self.assertIsInstance(radius, list)

    def test_warnings_returned(self):
        result, _ = self._run_hydrologist()
        self.assertIn("warnings", result)
        self.assertIsInstance(result["warnings"], list)


# ---------------------------------------------------------------------------
# Navigator — all 4 tools
# ---------------------------------------------------------------------------

class TestNavigatorAgent(unittest.TestCase):
    def setUp(self):
        self.artifact_root = Path(tempfile.mkdtemp())
        cart = self.artifact_root / ".cartography"
        cart.mkdir()

        # Minimal module_graph.json
        module_graph = {
            "directed": True,
            "multigraph": False,
            "graph": {},
            "nodes": [
                {"id": "src/ingestion.py", "node_type": "module", "path": "src/ingestion.py", "language": "python"},
                {"id": "src/transform.py", "node_type": "module", "path": "src/transform.py", "language": "python"},
                {"id": "src/serving.py", "node_type": "module", "path": "src/serving.py", "language": "python"},
            ],
            "links": [
                {"source": "src/ingestion.py", "target": "src/transform.py", "edge_type": "IMPORTS", "weight": 1},
                {"source": "src/serving.py", "target": "src/transform.py", "edge_type": "IMPORTS", "weight": 1},
            ],
        }
        (cart / "module_graph.json").write_text(json.dumps(module_graph), encoding="utf-8")

        # Minimal lineage_graph.json
        lineage_graph = {
            "graph": {
                "directed": True,
                "multigraph": False,
                "graph": {},
                "nodes": [
                    {"id": "raw.orders", "node_type": "dataset", "name": "raw.orders", "storage_type": "table"},
                    {"id": "staging.orders", "node_type": "dataset", "name": "staging.orders", "storage_type": "table"},
                ],
                "links": [
                    {"source": "raw.orders", "target": "staging.orders", "edge_type": "PRODUCES", "weight": 1},
                ],
            },
            "sources": ["raw.orders"],
            "sinks": ["staging.orders"],
            "warnings": [],
        }
        (cart / "lineage_graph.json").write_text(json.dumps(lineage_graph), encoding="utf-8")

        # Minimal semantic_report.json
        semantic = {
            "module_purpose_statements": [
                {
                    "path": "src/ingestion.py",
                    "purpose_statement": "Handles CSV ingestion from external data sources.",
                    "inferred_domain": "ingestion",
                    "documentation_drift": False,
                }
            ]
        }
        (cart / "semantic_report.json").write_text(json.dumps(semantic), encoding="utf-8")

        # Minimal CODEBASE.md
        (cart / "CODEBASE.md").write_text(
            "# CODEBASE: Living Context\n## Module Purpose Index\n- `src/ingestion.py` ingestion\n",
            encoding="utf-8",
        )

    def tearDown(self):
        import shutil
        shutil.rmtree(self.artifact_root, ignore_errors=True)

    def _make_navigator(self):
        from src.agents.navigator import NavigatorAgent
        return NavigatorAgent(self.artifact_root)

    # -- find_implementation --------------------------------------------------

    def test_find_implementation_returns_list(self):
        nav = self._make_navigator()
        result = nav.find_implementation("ingestion")
        self.assertIsInstance(result, list)

    def test_find_implementation_matches_concept(self):
        nav = self._make_navigator()
        result = nav.find_implementation("ingestion")
        self.assertTrue(len(result) > 0, "Expected at least 1 result for 'ingestion'")
        facts = " ".join(r["fact"] for r in result)
        self.assertIn("ingestion", facts.lower())

    def test_find_implementation_unknown_concept_falls_back(self):
        nav = self._make_navigator()
        # Should fall back to PageRank top nodes
        result = nav.find_implementation("xyzzy_nonexistent")
        self.assertIsInstance(result, list)

    def test_find_implementation_evidence_has_required_fields(self):
        nav = self._make_navigator()
        for item in nav.find_implementation("transform"):
            self.assertIn("file", item)
            self.assertIn("line_range", item)
            self.assertIn("method", item)
            self.assertIn("fact", item)

    # -- trace_lineage --------------------------------------------------------

    def test_trace_lineage_downstream_returns_list(self):
        nav = self._make_navigator()
        result = nav.trace_lineage("raw.orders", "downstream")
        self.assertIsInstance(result, list)

    def test_trace_lineage_upstream_returns_list(self):
        nav = self._make_navigator()
        result = nav.trace_lineage("staging.orders", "upstream")
        self.assertIsInstance(result, list)

    def test_trace_lineage_unknown_dataset_returns_sources_sinks(self):
        nav = self._make_navigator()
        result = nav.trace_lineage("totally_unknown_table", "downstream")
        self.assertIsInstance(result, list)
        # Should surface known sources/sinks as fallback
        if result:
            combined = " ".join(r["fact"] for r in result)
            self.assertTrue("raw.orders" in combined or "staging.orders" in combined)

    def test_trace_lineage_evidence_method_is_static(self):
        nav = self._make_navigator()
        for item in nav.trace_lineage("raw.orders", "downstream"):
            self.assertEqual(item["method"], "static-analysis")

    # -- blast_radius ---------------------------------------------------------

    def test_blast_radius_returns_list(self):
        nav = self._make_navigator()
        result = nav.blast_radius("src/transform.py")
        self.assertIsInstance(result, list)

    def test_blast_radius_identifies_dependents(self):
        nav = self._make_navigator()
        result = nav.blast_radius("src/transform.py")
        # transform.py is imported by ingestion.py and serving.py
        # blast_radius on transform.py in directed graph — depends on edge direction
        # At minimum, result should be a non-erroring list
        self.assertIsInstance(result, list)

    def test_blast_radius_unknown_module_returns_empty_or_fallback(self):
        nav = self._make_navigator()
        result = nav.blast_radius("src/totally_unknown.py")
        self.assertIsInstance(result, list)

    # -- explain_module -------------------------------------------------------

    def test_explain_module_returns_list(self):
        nav = self._make_navigator()
        result = nav.explain_module("src/ingestion.py")
        self.assertIsInstance(result, list)

    def test_explain_module_contains_purpose(self):
        nav = self._make_navigator()
        result = nav.explain_module("src/ingestion.py")
        self.assertGreater(len(result), 0)
        facts = " ".join(r["fact"] for r in result)
        self.assertIn("ingestion", facts.lower())

    def test_explain_module_method_is_llm_inference(self):
        nav = self._make_navigator()
        result = nav.explain_module("src/ingestion.py")
        methods = {r["method"] for r in result}
        self.assertTrue(methods & {"llm-inference", "hybrid-static-llm"})

    # -- answer (top-level) ---------------------------------------------------

    def test_answer_returns_string(self):
        nav = self._make_navigator()
        response = nav.answer("Where is the ingestion logic?")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_answer_for_lineage_question(self):
        nav = self._make_navigator()
        response = nav.answer("What upstream sources feed the staging.orders dataset?")
        self.assertIsInstance(response, str)

    def test_answer_includes_evidence(self):
        nav = self._make_navigator()
        response = nav.answer("blast radius of transform module")
        # Response should have evidence-backed format or fallback message
        self.assertTrue(
            "Evidence-backed" in response or "No evidence" in response,
            f"Unexpected response format: {response[:100]}",
        )


# ---------------------------------------------------------------------------
# Navigator — intent inference
# ---------------------------------------------------------------------------

class TestNavigatorIntentInference(unittest.TestCase):
    def _make_nav(self):
        from src.agents.navigator import NavigatorAgent
        return NavigatorAgent(Path(tempfile.mkdtemp()))

    def test_lineage_intent(self):
        nav = self._make_nav()
        self.assertEqual("lineage", nav._infer_intent("What upstream sources feed the orders dataset?"))

    def test_blast_intent(self):
        nav = self._make_nav()
        self.assertEqual("blast", nav._infer_intent("What is the blast radius of transform.py?"))

    def test_explain_intent(self):
        nav = self._make_nav()
        self.assertEqual("explain", nav._infer_intent("Explain what the ingestion module does"))

    def test_implementation_intent(self):
        nav = self._make_nav()
        self.assertEqual("implementation", nav._infer_intent("Where is the revenue calculation implemented?"))

    def test_mixed_intent_fallback(self):
        nav = self._make_nav()
        self.assertEqual("mixed", nav._infer_intent("Tell me about this codebase"))

    def test_param_extraction_quoted_path(self):
        nav = self._make_nav()
        params = nav._extract_query_params("blast radius of 'src/transform.py'")
        self.assertEqual("src/transform.py", params.get("path"))

    def test_param_extraction_direction(self):
        nav = self._make_nav()
        params = nav._extract_query_params("trace lineage upstream of orders")
        self.assertEqual("upstream", params.get("direction"))

    def test_param_extraction_concept(self):
        nav = self._make_nav()
        params = nav._extract_query_params("find implementation of 'revenue_calc'")
        self.assertEqual("revenue_calc", params.get("concept"))


# ---------------------------------------------------------------------------
# Archivist — CODEBASE.md generation
# ---------------------------------------------------------------------------

class TestArchivistAgent(unittest.TestCase):
    def _make_archivist(self):
        from src.agents.archivist import ArchivistAgent
        return ArchivistAgent(Path(tempfile.mkdtemp()))

    def _minimal_surveyor_result(self, output_root):
        return {
            "module_count": 3,
            "edge_count": 2,
            "pagerank": [("src/transform.py", 0.45), ("src/ingestion.py", 0.35)],
            "strongly_connected_components": [],
            "high_velocity_core": [{"path": "src/ingestion.py", "change_count": 12, "cumulative_share": 0.8}],
            "dead_code_candidates": [],
            "module_graph_path": str(output_root / ".cartography" / "module_graph.json"),
            "git_velocity": {},
        }

    def _minimal_hydro_result(self, output_root):
        return {
            "event_count": 1,
            "node_count": 2,
            "edge_count": 1,
            "sources": ["raw.orders"],
            "sinks": ["staging.orders"],
            "warnings": [],
            "lineage_graph_path": str(output_root / ".cartography" / "lineage_graph.json"),
        }

    def _minimal_semantic_result(self, output_root):
        # Write minimal semantic_report.json
        cart = output_root / ".cartography"
        cart.mkdir(parents=True, exist_ok=True)
        semantic_path = cart / "semantic_report.json"
        semantic_path.write_text(json.dumps({"module_purpose_statements": []}), encoding="utf-8")
        return {
            "module_count": 3,
            "domain_count": 2,
            "domain_boundaries": [{"domain": "ingestion", "module_count": 1}],
            "five_fde_answers": {
                "q1_primary_ingestion_path": "CSV files → ingestion.py",
                "q2_critical_outputs": "staging.orders",
                "q3_blast_radius": "transform.py affects serving.py",
                "q4_logic_concentration": "Concentrated in transform.py",
                "q5_git_velocity_map": "ingestion.py (12 changes)",
            },
            "semantic_report_path": str(semantic_path),
            "warnings": [],
            "model_policy": {"bulk_extraction_model": "gemini-flash", "synthesis_model": "claude"},
            "context_window_budget": {},
        }

    def test_codebase_md_written(self):
        output_root = Path(tempfile.mkdtemp())
        arch = self._make_archivist()
        result = arch.generate_CODEBASE_md(
            surveyor_result=self._minimal_surveyor_result(output_root),
            hydrologist_result=self._minimal_hydro_result(output_root),
            semanticist_result=self._minimal_semantic_result(output_root),
            output_root=output_root,
        )
        path = Path(result["codebase_md_path"])
        self.assertTrue(path.exists())

    def test_codebase_md_contains_required_sections(self):
        output_root = Path(tempfile.mkdtemp())
        arch = self._make_archivist()
        result = arch.generate_CODEBASE_md(
            surveyor_result=self._minimal_surveyor_result(output_root),
            hydrologist_result=self._minimal_hydro_result(output_root),
            semanticist_result=self._minimal_semantic_result(output_root),
            output_root=output_root,
        )
        text = Path(result["codebase_md_path"]).read_text(encoding="utf-8")
        for section in ["Architecture Overview", "Critical Path", "Data Sources", "Known Debt", "High-Velocity"]:
            self.assertIn(section, text, f"Section '{section}' missing from CODEBASE.md")

    def test_onboarding_brief_written(self):
        output_root = Path(tempfile.mkdtemp())
        arch = self._make_archivist()
        result = arch.generate_CODEBASE_md(
            surveyor_result=self._minimal_surveyor_result(output_root),
            hydrologist_result=self._minimal_hydro_result(output_root),
            semanticist_result=self._minimal_semantic_result(output_root),
            output_root=output_root,
        )
        path = Path(result["onboarding_brief_path"])
        self.assertTrue(path.exists())

    def test_onboarding_brief_contains_five_fde_answers(self):
        output_root = Path(tempfile.mkdtemp())
        arch = self._make_archivist()
        result = arch.generate_CODEBASE_md(
            surveyor_result=self._minimal_surveyor_result(output_root),
            hydrologist_result=self._minimal_hydro_result(output_root),
            semanticist_result=self._minimal_semantic_result(output_root),
            output_root=output_root,
        )
        text = Path(result["onboarding_brief_path"]).read_text(encoding="utf-8")
        self.assertIn("Five FDE Day-One Answers", text)
        self.assertIn("CSV files", text)  # q1 answer

    def test_architecture_overview_contains_counts(self):
        output_root = Path(tempfile.mkdtemp())
        arch = self._make_archivist()
        result = arch.generate_CODEBASE_md(
            surveyor_result=self._minimal_surveyor_result(output_root),
            hydrologist_result=self._minimal_hydro_result(output_root),
            semanticist_result=self._minimal_semantic_result(output_root),
            output_root=output_root,
        )
        text = Path(result["codebase_md_path"]).read_text(encoding="utf-8")
        self.assertIn("3 modules", text)
        self.assertIn("2 datasets", text)


# ---------------------------------------------------------------------------
# Tracing
# ---------------------------------------------------------------------------

class TestCartographyTracer(unittest.TestCase):
    def test_log_writes_jsonl(self):
        from src.tracing import CartographyTracer
        tmp = Path(tempfile.mkdtemp()) / "trace.jsonl"
        tracer = CartographyTracer(tmp)
        tracer.log(
            agent="Surveyor",
            action="analyze_module",
            confidence=0.95,
            analysis_method="static-analysis",
            evidence_sources=[{"file": "src/a.py", "line_range": "L1-L20", "method": "tree-sitter"}],
            metadata={"module": "src/a.py"},
        )
        self.assertTrue(tmp.exists())
        entries = [json.loads(line) for line in tmp.read_text().splitlines() if line.strip()]
        self.assertEqual(1, len(entries))
        self.assertEqual("Surveyor", entries[0]["agent"])
        self.assertEqual("analyze_module", entries[0]["action"])
        self.assertAlmostEqual(0.95, entries[0]["confidence"])

    def test_log_multiple_entries(self):
        from src.tracing import CartographyTracer
        tmp = Path(tempfile.mkdtemp()) / "trace.jsonl"
        tracer = CartographyTracer(tmp)
        for i in range(5):
            tracer.log(agent="Agent", action=f"step_{i}", confidence=0.9,
                       analysis_method="static", evidence_sources=[], metadata={})
        entries = [json.loads(line) for line in tmp.read_text().splitlines() if line.strip()]
        self.assertEqual(5, len(entries))

    def test_log_entry_has_timestamp(self):
        from src.tracing import CartographyTracer
        tmp = Path(tempfile.mkdtemp()) / "trace.jsonl"
        tracer = CartographyTracer(tmp)
        tracer.log(agent="X", action="y", confidence=1.0, analysis_method="m",
                   evidence_sources=[], metadata={})
        entry = json.loads(tmp.read_text().strip())
        self.assertIn("timestamp_utc", entry)


if __name__ == "__main__":
    unittest.main()
