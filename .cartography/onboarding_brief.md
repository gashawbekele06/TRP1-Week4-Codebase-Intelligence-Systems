# Onboarding Brief

## First 15 Minutes
This repository is organized as an analysis-focused architecture where static structure (8 modules, 4 import edges) is combined with data lineage (35 datasets, 36 lineage edges) and semantic domain inference (5 inferred domains) to provide operational intelligence for maintenance, risk assessment, and onboarding.

## Critical Modules to Read First
- `src/analyzers/tree_sitter_analyzer.py` (PageRank=0.2103)
- `src/agents/hydrologist.py` (PageRank=0.1291)
- `src/agents/semanticist.py` (PageRank=0.1291)
- `src/agents/surveyor.py` (PageRank=0.1291)
- `dashboard/src/app/api/cartography/route.ts` (PageRank=0.1006)

## Data Orientation
- Sources: ['env_file', 'file_path', 'graph_path', 'module_path', 'python_runtime:src\\agents\\hydrologist.py', 'subprocess:dynamic']
- Sinks: ['output_path', 'python_runtime:src\\analyzers\\tree_sitter_analyzer.py']

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
1. Primary Ingestion Path: Primary ingestion appears to flow from source datasets ['env_file', 'file_path', 'graph_path', 'module_path', 'python_runtime:src\\agents\\hydrologist.py'] into downstream transformations. Evidence: src/orchestrator.py:L19-L19; src/analyzers/tree_sitter_analyzer.py:L1-L200; src/agents/hydrologist.py:L1-L200
2. Most Critical Outputs: Most critical outputs are likely terminal lineage sinks ['output_path', 'python_runtime:src\\analyzers\\tree_sitter_analyzer.py'] and high-centrality modules from Surveyor PageRank. Evidence: src/orchestrator.py:L19-L19; src/analyzers/tree_sitter_analyzer.py:L1-L200; src/agents/hydrologist.py:L1-L200
3. Blast Radius if Critical Module Fails: Blast radius is highest around sink-producing transformations and architectural hubs; recently active files include ['README.md', 'src/agents/hydrologist.py', 'src/agents/surveyor.py', 'pyproject.toml', 'src/cli.py']. Evidence: src/orchestrator.py:L19-L19; src/analyzers/tree_sitter_analyzer.py:L1-L200; src/agents/hydrologist.py:L1-L200
4. Logic Concentration vs Distribution: Business logic is most concentrated in the inferred domain 'analysis-1', with representative modules ['src/agents/hydrologist.py', 'src/agents/semanticist.py', 'src/agents/surveyor.py']. Evidence: src/orchestrator.py:L19-L19; src/analyzers/tree_sitter_analyzer.py:L1-L200; src/agents/hydrologist.py:L1-L200
5. Git Velocity Hotspots: Git velocity hot spots are derived from Surveyor high-velocity core: ['README.md', 'src/agents/hydrologist.py', 'src/agents/surveyor.py', 'pyproject.toml', 'src/cli.py']; dead-code candidates identified: 1. Evidence: src/orchestrator.py:L19-L19; src/analyzers/tree_sitter_analyzer.py:L1-L200; src/agents/hydrologist.py:L1-L200