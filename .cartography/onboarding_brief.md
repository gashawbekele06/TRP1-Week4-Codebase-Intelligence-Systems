# Onboarding Brief

## First 15 Minutes
This repository is organized as an analysis-focused architecture where static structure (6 modules, 7 import edges) is combined with data lineage (0 datasets, 0 lineage edges) and semantic domain inference (5 inferred domains) to provide operational intelligence for maintenance, risk assessment, and onboarding.

## Critical Modules to Read First
- `src/orchestrator.py` (PageRank=0.1995)
- `src/agents/hydrologist.py` (PageRank=0.1949)
- `src/agents/semanticist.py` (PageRank=0.1949)
- `src/agents/surveyor.py` (PageRank=0.1949)
- `src/agents/__init__.py` (PageRank=0.1078)

## Data Orientation
- Sources: none discovered
- Sinks: none discovered

## Likely Pain Points
- `README.md` (changes=7)
- `src/agents/surveyor.py` (changes=5)
- `src/cli.py` (changes=5)
- `src/graph/__pycache__/knowledge_graph.cpython-313.pyc` (changes=4)
- `src/agents/__pycache__/hydrologist.cpython-313.pyc` (changes=4)
- `src/agents/__pycache__/surveyor.cpython-313.pyc` (changes=4)
- `.cartography/module_graph.json` (changes=4)
- `pyproject.toml` (changes=4)

## Week-One Focus
1. Validate critical path modules and their dependencies.
2. Confirm lineage sources/sinks against production expectations.
3. Address top debt items (cycles + documentation drift).