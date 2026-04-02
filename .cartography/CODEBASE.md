# CODEBASE: Living Context

## Architecture Overview
This repository is organized as an analysis-focused architecture where static structure (3 modules, 0 import edges) is combined with data lineage (0 datasets, 0 lineage edges) and semantic domain inference (4 inferred domains) to provide operational intelligence for maintenance, risk assessment, and onboarding.

## Critical Path (Top 5 by PageRank)
1. `src\agents\hydrologist.py` — PageRank `0.3333` [static-analysis]
2. `src\agents\navigator.py` — PageRank `0.3333` [static-analysis]
3. `tests\test_agents.py` — PageRank `0.3333` [static-analysis]

## Data Sources & Sinks
### Sources
- No lineage sources discovered.

### Sinks
- No lineage sinks discovered.

## Known Debt
### Circular Dependencies
- No circular dependency groups discovered.

### Documentation Drift Flags
- No documentation drift flags discovered.

## High-Velocity Files
- `README.md` — changes=10, cumulative_share=0.0592 [static-analysis]
- `.cartography/module_graph.json` — changes=7, cumulative_share=0.1006 [static-analysis]
- `pyproject.toml` — changes=6, cumulative_share=0.1361 [static-analysis]
- `src/agents/hydrologist.py` — changes=6, cumulative_share=0.1716 [static-analysis]
- `src/cli.py` — changes=6, cumulative_share=0.2071 [static-analysis]
- `src/agents/surveyor.py` — changes=5, cumulative_share=0.2367 [static-analysis]
- `.cartography/CODEBASE.md` — changes=4, cumulative_share=0.2604 [static-analysis]
- `.cartography/cartography_trace.jsonl` — changes=4, cumulative_share=0.284 [static-analysis]
- `.cartography/run_state.json` — changes=4, cumulative_share=0.3077 [static-analysis]
- `.cartography/semantic_report.json` — changes=4, cumulative_share=0.3314 [static-analysis]
- `src/agents/navigator.py` — changes=4, cumulative_share=0.355 [static-analysis]
- `.cartography/lineage_graph.json` — changes=4, cumulative_share=0.3787 [static-analysis]
- `src/orchestrator.py` — changes=4, cumulative_share=0.4024 [static-analysis]
- `src/graph/__pycache__/knowledge_graph.cpython-313.pyc` — changes=4, cumulative_share=0.426 [static-analysis]
- `src/agents/__pycache__/hydrologist.cpython-313.pyc` — changes=4, cumulative_share=0.4497 [static-analysis]
- `src/agents/__pycache__/surveyor.cpython-313.pyc` — changes=4, cumulative_share=0.4734 [static-analysis]
- `src/agents/semanticist.py` — changes=4, cumulative_share=0.497 [static-analysis]
- `src/__pycache__/cli.cpython-313.pyc` — changes=4, cumulative_share=0.5207 [static-analysis]
- `.cartography/onboarding_brief.md` — changes=3, cumulative_share=0.5385 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/PKG-INFO` — changes=3, cumulative_share=0.5562 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/SOURCES.txt` — changes=3, cumulative_share=0.574 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/requires.txt` — changes=3, cumulative_share=0.5917 [static-analysis]
- `src/agents/archivist.py` — changes=3, cumulative_share=0.6095 [static-analysis]
- `src/models/__pycache__/__init__.cpython-313.pyc` — changes=3, cumulative_share=0.6272 [static-analysis]
- `src/agents/__pycache__/__init__.cpython-313.pyc` — changes=3, cumulative_share=0.645 [static-analysis]
- `src/agents/__init__.py` — changes=3, cumulative_share=0.6627 [static-analysis]
- `src/graph/knowledge_graph.py` — changes=3, cumulative_share=0.6805 [static-analysis]
- `src/analyzers/__pycache__/python_dataflow.cpython-313.pyc` — changes=3, cumulative_share=0.6982 [static-analysis]
- `src/analyzers/__pycache__/tree_sitter_analyzer.cpython-313.pyc` — changes=3, cumulative_share=0.716 [static-analysis]
- `tests/test_agents.py` — changes=2, cumulative_share=0.7278 [static-analysis]
- `uv.lock` — changes=2, cumulative_share=0.7396 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/dependency_links.txt` — changes=2, cumulative_share=0.7515 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/entry_points.txt` — changes=2, cumulative_share=0.7633 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/top_level.txt` — changes=2, cumulative_share=0.7751 [static-analysis]
- `.cartography/navigator_agent.json` — changes=2, cumulative_share=0.787 [static-analysis]
- `src/models/__pycache__/graph.cpython-313.pyc` — changes=2, cumulative_share=0.7988 [static-analysis]
- `src/models/__pycache__/lineage.cpython-313.pyc` — changes=2, cumulative_share=0.8107 [static-analysis]

## Module Purpose Index
- `README.md` [domain=ingestion] — This module supports the codebase by owning line:# TRP1 Week 4: Brownfield Cartographer, line:A multi-agent codebase intelligence system that ingests any GitHub repository or, line:## Quick Start. Its business value is enabling consistent system behavior for the capability represented by README. [method=llm-inference]
- `src/agents/hydrologist.py` [domain=analysis] — This module supports the codebase by owning import_from:__future__, import:json, import_from:pathlib. Its business value is enabling consistent system behavior for the capability represented by hydrologist. [method=llm-inference]
- `src/agents/navigator.py` [domain=analysis] — This module supports the codebase by owning import_from:__future__, import:json, import:re. Its business value is enabling consistent system behavior for the capability represented by navigator. [method=llm-inference]
- `tests/test_agents.py` [domain=monitoring] — This module supports the codebase by owning import_from:__future__, import:json, import:tempfile. Its business value is enabling consistent system behavior for the capability represented by test_agents. [method=llm-inference]
