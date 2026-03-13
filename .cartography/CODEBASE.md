# CODEBASE: Living Context

## Architecture Overview
This repository is organized as an analysis-focused architecture where static structure (6 modules, 7 import edges) is combined with data lineage (0 datasets, 0 lineage edges) and semantic domain inference (5 inferred domains) to provide operational intelligence for maintenance, risk assessment, and onboarding.

## Critical Path (Top 5 by PageRank)
1. `src/orchestrator.py` — PageRank `0.1995` [static-analysis]
2. `src/agents/hydrologist.py` — PageRank `0.1949` [static-analysis]
3. `src/agents/semanticist.py` — PageRank `0.1949` [static-analysis]
4. `src/agents/surveyor.py` — PageRank `0.1949` [static-analysis]
5. `src/agents/__init__.py` — PageRank `0.1078` [static-analysis]

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
- `README.md` — changes=7, cumulative_share=0.0556 [static-analysis]
- `src/agents/surveyor.py` — changes=5, cumulative_share=0.0952 [static-analysis]
- `src/cli.py` — changes=5, cumulative_share=0.1349 [static-analysis]
- `src/graph/__pycache__/knowledge_graph.cpython-313.pyc` — changes=4, cumulative_share=0.1667 [static-analysis]
- `src/agents/__pycache__/hydrologist.cpython-313.pyc` — changes=4, cumulative_share=0.1984 [static-analysis]
- `src/agents/__pycache__/surveyor.cpython-313.pyc` — changes=4, cumulative_share=0.2302 [static-analysis]
- `.cartography/module_graph.json` — changes=4, cumulative_share=0.2619 [static-analysis]
- `pyproject.toml` — changes=4, cumulative_share=0.2937 [static-analysis]
- `src/agents/hydrologist.py` — changes=4, cumulative_share=0.3254 [static-analysis]
- `src/agents/semanticist.py` — changes=4, cumulative_share=0.3571 [static-analysis]
- `src/__pycache__/cli.cpython-313.pyc` — changes=4, cumulative_share=0.3889 [static-analysis]
- `src/models/__pycache__/__init__.cpython-313.pyc` — changes=3, cumulative_share=0.4127 [static-analysis]
- `src/agents/__pycache__/__init__.cpython-313.pyc` — changes=3, cumulative_share=0.4365 [static-analysis]
- `.cartography/lineage_graph.json` — changes=3, cumulative_share=0.4603 [static-analysis]
- `src/agents/__init__.py` — changes=3, cumulative_share=0.4841 [static-analysis]
- `src/orchestrator.py` — changes=3, cumulative_share=0.5079 [static-analysis]
- `src/graph/knowledge_graph.py` — changes=3, cumulative_share=0.5317 [static-analysis]
- `src/analyzers/__pycache__/python_dataflow.cpython-313.pyc` — changes=3, cumulative_share=0.5556 [static-analysis]
- `src/analyzers/__pycache__/tree_sitter_analyzer.cpython-313.pyc` — changes=3, cumulative_share=0.5794 [static-analysis]
- `src/models/__pycache__/graph.cpython-313.pyc` — changes=2, cumulative_share=0.5952 [static-analysis]
- `src/models/__pycache__/lineage.cpython-313.pyc` — changes=2, cumulative_share=0.6111 [static-analysis]
- `src/models/__pycache__/module.cpython-313.pyc` — changes=2, cumulative_share=0.627 [static-analysis]
- `src/graph/__pycache__/__init__.cpython-313.pyc` — changes=2, cumulative_share=0.6429 [static-analysis]
- `src/__pycache__/__init__.cpython-313.pyc` — changes=2, cumulative_share=0.6587 [static-analysis]
- `src/__pycache__/orchestrator.cpython-313.pyc` — changes=2, cumulative_share=0.6746 [static-analysis]
- `src/analyzers/__pycache__/dag_config_parser.cpython-313.pyc` — changes=2, cumulative_share=0.6905 [static-analysis]
- `src/analyzers/__pycache__/sql_lineage.cpython-313.pyc` — changes=2, cumulative_share=0.7063 [static-analysis]
- `src/analyzers/tree_sitter_analyzer.py` — changes=2, cumulative_share=0.7222 [static-analysis]
- `src/models/__init__.py` — changes=2, cumulative_share=0.7381 [static-analysis]
- `src/analyzers/python_dataflow.py` — changes=2, cumulative_share=0.754 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/PKG-INFO` — changes=2, cumulative_share=0.7698 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/SOURCES.txt` — changes=2, cumulative_share=0.7857 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/requires.txt` — changes=2, cumulative_share=0.8016 [static-analysis]
