# CODEBASE: Living Context

## Architecture Overview
This repository is organized as an analysis-focused architecture where static structure (23 modules, 0 import edges) is combined with data lineage (0 datasets, 0 lineage edges) and semantic domain inference (5 inferred domains) to provide operational intelligence for maintenance, risk assessment, and onboarding.

## Critical Path (Top 5 by PageRank)
1. `main.py` — PageRank `0.0435` [static-analysis]
2. `src\__init__.py` — PageRank `0.0435` [static-analysis]
3. `src\agents\__init__.py` — PageRank `0.0435` [static-analysis]
4. `src\agents\archivist.py` — PageRank `0.0435` [static-analysis]
5. `src\agents\hydrologist.py` — PageRank `0.0435` [static-analysis]

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
- `README.md` — changes=9, cumulative_share=0.0573 [static-analysis]
- `.cartography/module_graph.json` — changes=6, cumulative_share=0.0955 [static-analysis]
- `src/cli.py` — changes=6, cumulative_share=0.1338 [static-analysis]
- `pyproject.toml` — changes=5, cumulative_share=0.1656 [static-analysis]
- `src/agents/hydrologist.py` — changes=5, cumulative_share=0.1975 [static-analysis]
- `src/agents/surveyor.py` — changes=5, cumulative_share=0.2293 [static-analysis]
- `.cartography/lineage_graph.json` — changes=4, cumulative_share=0.2548 [static-analysis]
- `src/orchestrator.py` — changes=4, cumulative_share=0.2803 [static-analysis]
- `src/graph/__pycache__/knowledge_graph.cpython-313.pyc` — changes=4, cumulative_share=0.3057 [static-analysis]
- `src/agents/__pycache__/hydrologist.cpython-313.pyc` — changes=4, cumulative_share=0.3312 [static-analysis]
- `src/agents/__pycache__/surveyor.cpython-313.pyc` — changes=4, cumulative_share=0.3567 [static-analysis]
- `src/agents/semanticist.py` — changes=4, cumulative_share=0.3822 [static-analysis]
- `src/__pycache__/cli.cpython-313.pyc` — changes=4, cumulative_share=0.4076 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/PKG-INFO` — changes=3, cumulative_share=0.4268 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/SOURCES.txt` — changes=3, cumulative_share=0.4459 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/requires.txt` — changes=3, cumulative_share=0.465 [static-analysis]
- `.cartography/CODEBASE.md` — changes=3, cumulative_share=0.4841 [static-analysis]
- `.cartography/cartography_trace.jsonl` — changes=3, cumulative_share=0.5032 [static-analysis]
- `.cartography/run_state.json` — changes=3, cumulative_share=0.5223 [static-analysis]
- `.cartography/semantic_report.json` — changes=3, cumulative_share=0.5414 [static-analysis]
- `src/agents/archivist.py` — changes=3, cumulative_share=0.5605 [static-analysis]
- `src/agents/navigator.py` — changes=3, cumulative_share=0.5796 [static-analysis]
- `src/models/__pycache__/__init__.cpython-313.pyc` — changes=3, cumulative_share=0.5987 [static-analysis]
- `src/agents/__pycache__/__init__.cpython-313.pyc` — changes=3, cumulative_share=0.6178 [static-analysis]
- `src/agents/__init__.py` — changes=3, cumulative_share=0.6369 [static-analysis]
- `src/graph/knowledge_graph.py` — changes=3, cumulative_share=0.6561 [static-analysis]
- `src/analyzers/__pycache__/python_dataflow.cpython-313.pyc` — changes=3, cumulative_share=0.6752 [static-analysis]
- `src/analyzers/__pycache__/tree_sitter_analyzer.cpython-313.pyc` — changes=3, cumulative_share=0.6943 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/dependency_links.txt` — changes=2, cumulative_share=0.707 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/entry_points.txt` — changes=2, cumulative_share=0.7197 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/top_level.txt` — changes=2, cumulative_share=0.7325 [static-analysis]
- `.cartography/onboarding_brief.md` — changes=2, cumulative_share=0.7452 [static-analysis]
- `.cartography/navigator_agent.json` — changes=2, cumulative_share=0.758 [static-analysis]
- `src/models/__pycache__/graph.cpython-313.pyc` — changes=2, cumulative_share=0.7707 [static-analysis]
- `src/models/__pycache__/lineage.cpython-313.pyc` — changes=2, cumulative_share=0.7834 [static-analysis]
- `src/models/__pycache__/module.cpython-313.pyc` — changes=2, cumulative_share=0.7962 [static-analysis]
- `src/graph/__pycache__/__init__.cpython-313.pyc` — changes=2, cumulative_share=0.8089 [static-analysis]

## Module Purpose Index
- `main.py` [domain=orchestration] — This module supports the codebase by owning import_from:src.cli, file:main.py. Its business value is enabling consistent system behavior for the capability represented by main. [method=llm-inference]
- `README.md` [domain=ingestion] — This module supports the codebase by owning line:# TRP1 Week 4: Brownfield Cartographer, line:A multi-agent codebase intelligence system that ingests any GitHub repository or, line:## Quick Start. Its business value is enabling consistent system behavior for the capability represented by README. [method=llm-inference]
- `RECONNAISSANCE.md` [domain=transformation] — This module supports the codebase by owning line:# RECONNAISSANCE: dbt-labs/jaffle-shop (classic), line:Target repo: https://github.com/dbt-labs/jaffle-shop-classic (redirected from ht, line:This is a small, self-contained dbt project that models a fictional e‑commerce s. Its business value is enabling consistent system behavior for the capability represented by RECONNAISSANCE. [method=llm-inference]
- `src/__init__.py` [domain=ingestion] — This module supports the codebase by owning line:"""Brownfield Cartographer source package.""", file:__init__.py. Its business value is enabling consistent system behavior for the capability represented by __init__. [method=llm-inference]
- `src/agents/__init__.py` [domain=ingestion] — This module supports the codebase by owning import_from:src.agents.archivist, import_from:src.agents.hydrologist, import_from:src.agents.navigator. Its business value is enabling consistent system behavior for the capability represented by __init__. [method=llm-inference]
- `src/agents/archivist.py` [domain=ingestion] — This module supports the codebase by owning import_from:__future__, import_from:pathlib, import_from:src.tracing. Its business value is enabling consistent system behavior for the capability represented by archivist. [method=llm-inference]
- `src/agents/hydrologist.py` [domain=ingestion] — This module supports the codebase by owning import_from:__future__, import:json, import_from:pathlib. Its business value is enabling consistent system behavior for the capability represented by hydrologist. [method=llm-inference]
- `src/agents/navigator.py` [domain=ingestion] — This module supports the codebase by owning import_from:__future__, import:json, import:re. Its business value is enabling consistent system behavior for the capability represented by navigator. [method=llm-inference]
- `src/agents/semanticist.py` [domain=ingestion] — This module supports the codebase by owning import_from:__future__, import:ast, import:json. Its business value is enabling consistent system behavior for the capability represented by semanticist. [method=llm-inference]
- `src/agents/surveyor.py` [domain=ingestion] — This module supports the codebase by owning import_from:__future__, import:subprocess, import_from:collections. Its business value is enabling consistent system behavior for the capability represented by surveyor. [method=llm-inference]
- `src/analyzers/dag_config_parser.py` [domain=transformation] — This module supports the codebase by owning import_from:__future__, import_from:pathlib, import:yaml. Its business value is enabling consistent system behavior for the capability represented by dag_config_parser. [method=llm-inference]
- `src/analyzers/python_dataflow.py` [domain=transformation] — This module supports the codebase by owning import_from:__future__, import:ast, import_from:pathlib. Its business value is enabling consistent system behavior for the capability represented by python_dataflow. [method=llm-inference]
- `src/analyzers/sql_lineage.py` [domain=transformation] — This module supports the codebase by owning import_from:__future__, import:re, import_from:pathlib. Its business value is enabling consistent system behavior for the capability represented by sql_lineage. [method=llm-inference]
- `src/analyzers/tree_sitter_analyzer.py` [domain=transformation] — This module supports the codebase by owning import_from:__future__, import:ast, import_from:pathlib. Its business value is enabling consistent system behavior for the capability represented by tree_sitter_analyzer. [method=llm-inference]
- `src/cli.py` [domain=ingestion] — This module supports the codebase by owning import_from:__future__, import:argparse, import_from:pathlib. Its business value is enabling consistent system behavior for the capability represented by cli. [method=llm-inference]
- `src/graph/__init__.py` [domain=transformation] — This module supports the codebase by owning line:"""Knowledge graph utilities.""", file:__init__.py. Its business value is enabling consistent system behavior for the capability represented by __init__. [method=llm-inference]
- `src/graph/knowledge_graph.py` [domain=transformation] — This module supports the codebase by owning import_from:__future__, import:json, import_from:pathlib. Its business value is enabling consistent system behavior for the capability represented by knowledge_graph. [method=llm-inference]
- `src/models/__init__.py` [domain=transformation] — This module supports the codebase by owning import_from:src.models.graph, import_from:src.models.lineage, import_from:src.models.module. Its business value is enabling consistent system behavior for the capability represented by __init__. [method=llm-inference]
- `src/models/graph.py` [domain=transformation] — This module supports the codebase by owning import_from:__future__, import_from:datetime, import_from:typing. Its business value is enabling consistent system behavior for the capability represented by graph. [method=llm-inference]
- `src/models/lineage.py` [domain=transformation] — This module supports the codebase by owning import_from:__future__, import_from:pydantic, class:TransformationEvent. Its business value is enabling consistent system behavior for the capability represented by lineage. [method=llm-inference]
- `src/models/module.py` [domain=transformation] — This module supports the codebase by owning import_from:__future__, import_from:pydantic, class:FunctionInfo. Its business value is enabling consistent system behavior for the capability represented by module. [method=llm-inference]
- `src/orchestrator.py` [domain=ingestion] — This module supports the codebase by owning import_from:__future__, import:json, import:shutil. Its business value is enabling consistent system behavior for the capability represented by orchestrator. [method=llm-inference]
- `src/tracing.py` [domain=ingestion] — This module supports the codebase by owning import_from:__future__, import:json, import_from:dataclasses. Its business value is enabling consistent system behavior for the capability represented by tracing. [method=llm-inference]
- `tests/test_agents.py` [domain=serving] — This module supports the codebase by owning import_from:__future__, import:json, import:tempfile. Its business value is enabling consistent system behavior for the capability represented by test_agents. [method=llm-inference]
- `tests/test_knowledge_graph_deserialization.py` [domain=serving] — This module supports the codebase by owning import_from:__future__, import:json, import:tempfile. Its business value is enabling consistent system behavior for the capability represented by test_knowledge_graph_deserialization. [method=llm-inference]
