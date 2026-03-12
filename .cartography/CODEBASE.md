# CODEBASE: Living Context

## Architecture Overview
This repository is organized as an analysis-focused architecture where static structure (22 modules, 36 import edges) is combined with data lineage (0 datasets, 0 lineage edges) and semantic domain inference (5 inferred domains) to provide operational intelligence for maintenance, risk assessment, and onboarding.

## Critical Path (Top 5 by PageRank)
1. `src/tracing.py` — PageRank `0.1459` [static-analysis]
2. `src/models/lineage.py` — PageRank `0.0997` [static-analysis]
3. `src/models/module.py` — PageRank `0.0752` [static-analysis]
4. `src/models/graph.py` — PageRank `0.0745` [static-analysis]
5. `src/agents/navigator.py` — PageRank `0.0529` [static-analysis]

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
- `README.md` — changes=6, cumulative_share=0.0606 [static-analysis]
- `src/agents/surveyor.py` — changes=4, cumulative_share=0.101 [static-analysis]
- `src/cli.py` — changes=4, cumulative_share=0.1414 [static-analysis]
- `src/__pycache__/cli.cpython-313.pyc` — changes=4, cumulative_share=0.1818 [static-analysis]
- `src/agents/hydrologist.py` — changes=3, cumulative_share=0.2121 [static-analysis]
- `src/agents/semanticist.py` — changes=3, cumulative_share=0.2424 [static-analysis]
- `src/graph/__pycache__/knowledge_graph.cpython-313.pyc` — changes=3, cumulative_share=0.2727 [static-analysis]
- `src/graph/knowledge_graph.py` — changes=3, cumulative_share=0.303 [static-analysis]
- `src/analyzers/__pycache__/python_dataflow.cpython-313.pyc` — changes=3, cumulative_share=0.3333 [static-analysis]
- `src/analyzers/__pycache__/tree_sitter_analyzer.cpython-313.pyc` — changes=3, cumulative_share=0.3636 [static-analysis]
- `.cartography/module_graph.json` — changes=3, cumulative_share=0.3939 [static-analysis]
- `pyproject.toml` — changes=3, cumulative_share=0.4242 [static-analysis]
- `src/agents/__init__.py` — changes=2, cumulative_share=0.4444 [static-analysis]
- `src/orchestrator.py` — changes=2, cumulative_share=0.4646 [static-analysis]
- `src/__pycache__/__init__.cpython-313.pyc` — changes=2, cumulative_share=0.4848 [static-analysis]
- `src/__pycache__/orchestrator.cpython-313.pyc` — changes=2, cumulative_share=0.5051 [static-analysis]
- `src/analyzers/__pycache__/dag_config_parser.cpython-313.pyc` — changes=2, cumulative_share=0.5253 [static-analysis]
- `src/analyzers/__pycache__/sql_lineage.cpython-313.pyc` — changes=2, cumulative_share=0.5455 [static-analysis]
- `src/analyzers/tree_sitter_analyzer.py` — changes=2, cumulative_share=0.5657 [static-analysis]
- `src/agents/__pycache__/hydrologist.cpython-313.pyc` — changes=2, cumulative_share=0.5859 [static-analysis]
- `src/agents/__pycache__/surveyor.cpython-313.pyc` — changes=2, cumulative_share=0.6061 [static-analysis]
- `src/models/__pycache__/__init__.cpython-313.pyc` — changes=2, cumulative_share=0.6263 [static-analysis]
- `.cartography/lineage_graph.json` — changes=2, cumulative_share=0.6465 [static-analysis]
- `src/models/__init__.py` — changes=2, cumulative_share=0.6667 [static-analysis]
- `src/analyzers/python_dataflow.py` — changes=2, cumulative_share=0.6869 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/PKG-INFO` — changes=2, cumulative_share=0.7071 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/SOURCES.txt` — changes=2, cumulative_share=0.7273 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/requires.txt` — changes=2, cumulative_share=0.7475 [static-analysis]
- `main.py` — changes=2, cumulative_share=0.7677 [static-analysis]
- `src/agents/navigator.py` — changes=1, cumulative_share=0.7778 [static-analysis]
- `src/agents/archivist.py` — changes=1, cumulative_share=0.7879 [static-analysis]
- `src/tracing.py` — changes=1, cumulative_share=0.798 [static-analysis]
- `tests/test_knowledge_graph_deserialization.py` — changes=1, cumulative_share=0.8081 [static-analysis]
