# Onboarding Brief

## First 15 Minutes
This repository is organized as an analysis-focused architecture where static structure (4 modules, 4 import edges) is combined with data lineage (0 datasets, 0 lineage edges) and semantic domain inference (5 inferred domains) to provide operational intelligence for maintenance, risk assessment, and onboarding.

## Critical Modules to Read First
- `src/agents/navigator.py` (PageRank=0.3350)
- `src/agents/archivist.py` (PageRank=0.2649)
- `src/orchestrator.py` (PageRank=0.2351)
- `src/cli.py` (PageRank=0.1650)

## Data Orientation
- Sources: none discovered
- Sinks: none discovered

## Likely Pain Points
- `README.md` (changes=8)
- `src/cli.py` (changes=6)
- `.cartography/module_graph.json` (changes=5)
- `src/agents/surveyor.py` (changes=5)
- `src/orchestrator.py` (changes=4)
- `src/graph/__pycache__/knowledge_graph.cpython-313.pyc` (changes=4)
- `src/agents/__pycache__/hydrologist.cpython-313.pyc` (changes=4)
- `src/agents/__pycache__/surveyor.cpython-313.pyc` (changes=4)

## Week-One Focus
1. Validate critical path modules and their dependencies.
2. Confirm lineage sources/sinks against production expectations.
3. Address top debt items (cycles + documentation drift).

## Five FDE Day-One Answers
1. Primary Ingestion Path: Primary ingestion appears to flow from source datasets not explicitly discovered into downstream transformations. Evidence: src/agents/navigator.py:L16-L16; src/agents/navigator.py:L1-L200; src/agents/archivist.py:L1-L200
2. Most Critical Outputs: Most critical outputs are likely terminal lineage sinks not explicitly discovered and high-centrality modules from Surveyor PageRank. Evidence: src/agents/navigator.py:L16-L16; src/agents/navigator.py:L1-L200; src/agents/archivist.py:L1-L200
3. Blast Radius if Critical Module Fails: Blast radius is highest around sink-producing transformations and architectural hubs; recently active files include ['README.md', 'src/cli.py', '.cartography/module_graph.json', 'src/agents/surveyor.py', 'src/orchestrator.py']. Evidence: src/agents/navigator.py:L16-L16; src/agents/navigator.py:L1-L200; src/agents/archivist.py:L1-L200
4. Logic Concentration vs Distribution: Business logic is most concentrated in the inferred domain 'analysis', with representative modules ['README.md', 'src/agents/archivist.py', 'src/agents/navigator.py']. Evidence: src/agents/navigator.py:L16-L16; src/agents/navigator.py:L1-L200; src/agents/archivist.py:L1-L200
5. Git Velocity Hotspots: Git velocity hot spots are derived from Surveyor high-velocity core: ['README.md', 'src/cli.py', '.cartography/module_graph.json', 'src/agents/surveyor.py', 'src/orchestrator.py']; dead-code candidates identified: 1. Evidence: src/agents/navigator.py:L16-L16; src/agents/navigator.py:L1-L200; src/agents/archivist.py:L1-L200