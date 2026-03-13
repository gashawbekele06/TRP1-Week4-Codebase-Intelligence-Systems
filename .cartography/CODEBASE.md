# CODEBASE: Living Context

## Architecture Overview
This repository is organized as an analysis-focused architecture where static structure (4 modules, 4 import edges) is combined with data lineage (0 datasets, 0 lineage edges) and semantic domain inference (5 inferred domains) to provide operational intelligence for maintenance, risk assessment, and onboarding.

## Critical Path (Top 5 by PageRank)
1. `src/agents/navigator.py` — PageRank `0.3350` [static-analysis]
2. `src/agents/archivist.py` — PageRank `0.2649` [static-analysis]
3. `src/orchestrator.py` — PageRank `0.2351` [static-analysis]
4. `src/cli.py` — PageRank `0.1650` [static-analysis]

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
- `README.md` — changes=8, cumulative_share=0.058 [static-analysis]
- `src/cli.py` — changes=6, cumulative_share=0.1014 [static-analysis]
- `.cartography/module_graph.json` — changes=5, cumulative_share=0.1377 [static-analysis]
- `src/agents/surveyor.py` — changes=5, cumulative_share=0.1739 [static-analysis]
- `src/orchestrator.py` — changes=4, cumulative_share=0.2029 [static-analysis]
- `src/graph/__pycache__/knowledge_graph.cpython-313.pyc` — changes=4, cumulative_share=0.2319 [static-analysis]
- `src/agents/__pycache__/hydrologist.cpython-313.pyc` — changes=4, cumulative_share=0.2609 [static-analysis]
- `src/agents/__pycache__/surveyor.cpython-313.pyc` — changes=4, cumulative_share=0.2899 [static-analysis]
- `pyproject.toml` — changes=4, cumulative_share=0.3188 [static-analysis]
- `src/agents/hydrologist.py` — changes=4, cumulative_share=0.3478 [static-analysis]
- `src/agents/semanticist.py` — changes=4, cumulative_share=0.3768 [static-analysis]
- `src/__pycache__/cli.cpython-313.pyc` — changes=4, cumulative_share=0.4058 [static-analysis]
- `src/models/__pycache__/__init__.cpython-313.pyc` — changes=3, cumulative_share=0.4275 [static-analysis]
- `src/agents/__pycache__/__init__.cpython-313.pyc` — changes=3, cumulative_share=0.4493 [static-analysis]
- `.cartography/lineage_graph.json` — changes=3, cumulative_share=0.471 [static-analysis]
- `src/agents/__init__.py` — changes=3, cumulative_share=0.4928 [static-analysis]
- `src/graph/knowledge_graph.py` — changes=3, cumulative_share=0.5145 [static-analysis]
- `src/analyzers/__pycache__/python_dataflow.cpython-313.pyc` — changes=3, cumulative_share=0.5362 [static-analysis]
- `src/analyzers/__pycache__/tree_sitter_analyzer.cpython-313.pyc` — changes=3, cumulative_share=0.558 [static-analysis]
- `.cartography/CODEBASE.md` — changes=2, cumulative_share=0.5725 [static-analysis]
- `.cartography/cartography_trace.jsonl` — changes=2, cumulative_share=0.587 [static-analysis]
- `.cartography/navigator_agent.json` — changes=2, cumulative_share=0.6014 [static-analysis]
- `.cartography/run_state.json` — changes=2, cumulative_share=0.6159 [static-analysis]
- `.cartography/semantic_report.json` — changes=2, cumulative_share=0.6304 [static-analysis]
- `src/agents/archivist.py` — changes=2, cumulative_share=0.6449 [static-analysis]
- `src/agents/navigator.py` — changes=2, cumulative_share=0.6594 [static-analysis]
- `src/models/__pycache__/graph.cpython-313.pyc` — changes=2, cumulative_share=0.6739 [static-analysis]
- `src/models/__pycache__/lineage.cpython-313.pyc` — changes=2, cumulative_share=0.6884 [static-analysis]
- `src/models/__pycache__/module.cpython-313.pyc` — changes=2, cumulative_share=0.7029 [static-analysis]
- `src/graph/__pycache__/__init__.cpython-313.pyc` — changes=2, cumulative_share=0.7174 [static-analysis]
- `src/__pycache__/__init__.cpython-313.pyc` — changes=2, cumulative_share=0.7319 [static-analysis]
- `src/__pycache__/orchestrator.cpython-313.pyc` — changes=2, cumulative_share=0.7464 [static-analysis]
- `src/analyzers/__pycache__/dag_config_parser.cpython-313.pyc` — changes=2, cumulative_share=0.7609 [static-analysis]
- `src/analyzers/__pycache__/sql_lineage.cpython-313.pyc` — changes=2, cumulative_share=0.7754 [static-analysis]
- `src/analyzers/tree_sitter_analyzer.py` — changes=2, cumulative_share=0.7899 [static-analysis]
- `src/models/__init__.py` — changes=2, cumulative_share=0.8043 [static-analysis]

## Module Purpose Index
- `README.md` [domain=ingestion] — This module supports the codebase by owning line:# Brownfield Cartographer (Phase 1 + Phase 2 + Phase 3 + Phase 4), line:This repository now implements:, line:- **Phase 1: Surveyor Agent (Static Structure)**. Its business value is enabling consistent system behavior for the capability represented by README. [method=llm-inference]
- `src/agents/archivist.py` [domain=analysis] — This module supports the codebase by owning import_from:__future__, import_from:pathlib, import_from:src.tracing. Its business value is enabling consistent system behavior for the capability represented by archivist. [method=llm-inference]
- `src/agents/navigator.py` [domain=analysis] — This module supports the codebase by owning import_from:__future__, import:json, import:re. Its business value is enabling consistent system behavior for the capability represented by navigator. [method=llm-inference]
- `src/cli.py` [domain=orchestration] — This module supports the codebase by owning import_from:__future__, import:argparse, import_from:pathlib. Its business value is enabling consistent system behavior for the capability represented by cli. [method=llm-inference]
- `src/orchestrator.py` [domain=orchestration] — This module supports the codebase by owning import_from:__future__, import:json, import:shutil. Its business value is enabling consistent system behavior for the capability represented by orchestrator. [method=llm-inference]
