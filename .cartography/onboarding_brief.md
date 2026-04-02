# Onboarding Brief

## First 15 Minutes
This repository is organized as an analysis-focused architecture where static structure (3 modules, 0 import edges) is combined with data lineage (0 datasets, 0 lineage edges) and semantic domain inference (4 inferred domains) to provide operational intelligence for maintenance, risk assessment, and onboarding.

## Critical Modules to Read First
- `src\agents\hydrologist.py` (PageRank=0.3333)
- `src\agents\navigator.py` (PageRank=0.3333)
- `tests\test_agents.py` (PageRank=0.3333)

## Data Orientation
- Sources: none discovered
- Sinks: none discovered

## Likely Pain Points
- `README.md` (changes=10)
- `.cartography/module_graph.json` (changes=7)
- `pyproject.toml` (changes=6)
- `src/agents/hydrologist.py` (changes=6)
- `src/cli.py` (changes=6)
- `src/agents/surveyor.py` (changes=5)
- `.cartography/CODEBASE.md` (changes=4)
- `.cartography/cartography_trace.jsonl` (changes=4)

## Week-One Focus
1. Validate critical path modules and their dependencies.
2. Confirm lineage sources/sinks against production expectations.
3. Address top debt items (cycles + documentation drift).

## Five FDE Day-One Answers
1. Primary Ingestion Path: Primary ingestion appears to flow from source datasets not explicitly discovered into downstream transformations. Evidence: src\agents\navigator.py:L16-L16; tests\test_agents.py:L432-L432; tests\test_agents.py:L551-L551
2. Most Critical Outputs: Most critical outputs are likely terminal lineage sinks not explicitly discovered and high-centrality modules from Surveyor PageRank. Evidence: src\agents\navigator.py:L16-L16; tests\test_agents.py:L432-L432; tests\test_agents.py:L551-L551
3. Blast Radius if Critical Module Fails: Blast radius is highest around sink-producing transformations and architectural hubs; recently active files include ['README.md', '.cartography/module_graph.json', 'pyproject.toml', 'src/agents/hydrologist.py', 'src/cli.py']. Evidence: src\agents\navigator.py:L16-L16; tests\test_agents.py:L432-L432; tests\test_agents.py:L551-L551
4. Logic Concentration vs Distribution: Business logic is most concentrated in the inferred domain 'analysis', with representative modules ['README.md', 'src/agents/hydrologist.py', 'src/agents/navigator.py']. Evidence: src\agents\navigator.py:L16-L16; tests\test_agents.py:L432-L432; tests\test_agents.py:L551-L551
5. Git Velocity Hotspots: Git velocity hot spots are derived from Surveyor high-velocity core: ['README.md', '.cartography/module_graph.json', 'pyproject.toml', 'src/agents/hydrologist.py', 'src/cli.py']; dead-code candidates identified: 7. Evidence: src\agents\navigator.py:L16-L16; tests\test_agents.py:L432-L432; tests\test_agents.py:L551-L551