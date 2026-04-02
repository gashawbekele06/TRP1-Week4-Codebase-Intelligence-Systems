# Onboarding Brief

## First 15 Minutes
This repository is organized as an analysis-focused architecture where static structure (15 modules, 0 import edges) is combined with data lineage (0 datasets, 0 lineage edges) and semantic domain inference (5 inferred domains) to provide operational intelligence for maintenance, risk assessment, and onboarding.

## Critical Modules to Read First
- `dashboard\next.config.ts` (PageRank=0.0667)
- `dashboard\src\app\api\cartography\route.ts` (PageRank=0.0667)
- `dashboard\src\app\api\query\route.ts` (PageRank=0.0667)
- `dashboard\src\app\layout.tsx` (PageRank=0.0667)
- `dashboard\src\app\page.tsx` (PageRank=0.0667)

## Data Orientation
- Sources: none discovered
- Sinks: none discovered

## Likely Pain Points
- `README.md` (changes=10)
- `.cartography/module_graph.json` (changes=8)
- `pyproject.toml` (changes=6)
- `src/agents/hydrologist.py` (changes=6)
- `src/cli.py` (changes=6)
- `.cartography/CODEBASE.md` (changes=5)
- `.cartography/cartography_trace.jsonl` (changes=5)
- `.cartography/run_state.json` (changes=5)

## Week-One Focus
1. Validate critical path modules and their dependencies.
2. Confirm lineage sources/sinks against production expectations.
3. Address top debt items (cycles + documentation drift).

## Five FDE Day-One Answers
1. Primary Ingestion Path: Primary ingestion appears to flow from source datasets not explicitly discovered into downstream transformations. Evidence: dashboard\next.config.ts:L1-L200; dashboard\src\app\api\cartography\route.ts:L1-L200; dashboard\src\app\api\query\route.ts:L1-L200
2. Most Critical Outputs: Most critical outputs are likely terminal lineage sinks not explicitly discovered and high-centrality modules from Surveyor PageRank. Evidence: dashboard\next.config.ts:L1-L200; dashboard\src\app\api\cartography\route.ts:L1-L200; dashboard\src\app\api\query\route.ts:L1-L200
3. Blast Radius if Critical Module Fails: Blast radius is highest around sink-producing transformations and architectural hubs; recently active files include ['README.md', '.cartography/module_graph.json', 'pyproject.toml', 'src/agents/hydrologist.py', 'src/cli.py']. Evidence: dashboard\next.config.ts:L1-L200; dashboard\src\app\api\cartography\route.ts:L1-L200; dashboard\src\app\api\query\route.ts:L1-L200
4. Logic Concentration vs Distribution: Business logic is most concentrated in the inferred domain 'ingestion', with representative modules ['dashboard/AGENTS.md', 'dashboard/CLAUDE.md', 'dashboard/next.config.ts']. Evidence: dashboard\next.config.ts:L1-L200; dashboard\src\app\api\cartography\route.ts:L1-L200; dashboard\src\app\api\query\route.ts:L1-L200
5. Git Velocity Hotspots: Git velocity hot spots are derived from Surveyor high-velocity core: ['README.md', '.cartography/module_graph.json', 'pyproject.toml', 'src/agents/hydrologist.py', 'src/cli.py']; dead-code candidates identified: 0. Evidence: dashboard\next.config.ts:L1-L200; dashboard\src\app\api\cartography\route.ts:L1-L200; dashboard\src\app\api\query\route.ts:L1-L200