# Onboarding Brief

## First 15 Minutes
This repository is organized as an analysis-focused architecture where static structure (39 modules, 42 import edges) is combined with data lineage (94 datasets, 87 lineage edges) and semantic domain inference (7 inferred domains) to provide operational intelligence for maintenance, risk assessment, and onboarding.

## Critical Modules to Read First
- `src/tracing.py` (PageRank=0.1092)
- `src/models/lineage.py` (PageRank=0.0683)
- `src/models/graph.py` (PageRank=0.0560)
- `src/models/module.py` (PageRank=0.0532)
- `src/agents/navigator.py` (PageRank=0.0395)

## Data Orientation
- Sources: ['codebase_path', 'env_file', 'file_path', 'graph_path', 'input_path', 'module_path', 'python_runtime:src\\agents\\hydrologist.py', 'subprocess:dynamic']
- Sinks: ['onboarding_path', 'output_path', 'python_runtime:src\\agents\\navigator.py', 'python_runtime:src\\analyzers\\dag_config_parser.py', 'python_runtime:src\\analyzers\\python_dataflow.py', 'python_runtime:src\\analyzers\\sql_lineage.py', 'python_runtime:src\\analyzers\\tree_sitter_analyzer.py']

## Likely Pain Points
- `README.md` (changes=10)
- `src/agents/hydrologist.py` (changes=7)
- `src/agents/surveyor.py` (changes=6)
- `pyproject.toml` (changes=6)
- `src/cli.py` (changes=6)
- `src/agents/semanticist.py` (changes=5)
- `src/orchestrator.py` (changes=5)
- `src/agents/navigator.py` (changes=4)

## Week-One Focus
1. Validate critical path modules and their dependencies.
2. Confirm lineage sources/sinks against production expectations.
3. Address top debt items (cycles + documentation drift).

## Five FDE Day-One Answers
1. Primary Ingestion Path: Primary ingestion appears to flow from source datasets ['codebase_path', 'env_file', 'file_path', 'graph_path', 'input_path'] into downstream transformations. Evidence: src/agents/navigator.py:L16-L16; src/tracing.py:L1-L200; src/models/lineage.py:L1-L200
2. Most Critical Outputs: Most critical outputs are likely terminal lineage sinks ['onboarding_path', 'output_path', 'python_runtime:src\\agents\\navigator.py', 'python_runtime:src\\analyzers\\dag_config_parser.py', 'python_runtime:src\\analyzers\\python_dataflow.py'] and high-centrality modules from Surveyor PageRank. Evidence: src/agents/navigator.py:L16-L16; src/tracing.py:L1-L200; src/models/lineage.py:L1-L200
3. Blast Radius if Critical Module Fails: Blast radius is highest around sink-producing transformations and architectural hubs; recently active files include ['README.md', 'src/agents/hydrologist.py', 'src/agents/surveyor.py', 'pyproject.toml', 'src/cli.py']. Evidence: src/agents/navigator.py:L16-L16; src/tracing.py:L1-L200; src/models/lineage.py:L1-L200
4. Logic Concentration vs Distribution: Business logic is most concentrated in the inferred domain 'transformation-1', with representative modules ['src/agents/archivist.py', 'src/agents/hydrologist.py', 'src/agents/navigator.py']. Evidence: src/agents/navigator.py:L16-L16; src/tracing.py:L1-L200; src/models/lineage.py:L1-L200
5. Git Velocity Hotspots: Git velocity hot spots are derived from Surveyor high-velocity core: ['README.md', 'src/agents/hydrologist.py', 'src/agents/surveyor.py', 'pyproject.toml', 'src/cli.py']; dead-code candidates identified: 1. Evidence: src/agents/navigator.py:L16-L16; src/tracing.py:L1-L200; src/models/lineage.py:L1-L200