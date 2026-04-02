# CODEBASE: Living Context

## Architecture Overview
This repository is organized as an analysis-focused architecture where static structure (8 modules, 4 import edges) is combined with data lineage (35 datasets, 36 lineage edges) and semantic domain inference (5 inferred domains) to provide operational intelligence for maintenance, risk assessment, and onboarding.

## Critical Path (Top 5 by PageRank)
1. `src/analyzers/tree_sitter_analyzer.py` — PageRank `0.2103` [static-analysis]
2. `src/agents/hydrologist.py` — PageRank `0.1291` [static-analysis]
3. `src/agents/semanticist.py` — PageRank `0.1291` [static-analysis]
4. `src/agents/surveyor.py` — PageRank `0.1291` [static-analysis]
5. `dashboard/src/app/api/cartography/route.ts` — PageRank `0.1006` [static-analysis]

## Data Sources & Sinks
### Sources
- `env_file` [static-analysis]
- `file_path` [static-analysis]
- `graph_path` [static-analysis]
- `module_path` [static-analysis]
- `python_runtime:src\agents\hydrologist.py` [static-analysis]
- `subprocess:dynamic` [static-analysis]

### Sinks
- `output_path` [static-analysis]
- `python_runtime:src\analyzers\tree_sitter_analyzer.py` [static-analysis]

## Known Debt
### Circular Dependencies
- No circular dependency groups discovered.

### Documentation Drift Flags
- No documentation drift flags discovered.

## High-Velocity Files
- `README.md` — changes=10, cumulative_share=0.1266 [static-analysis]
- `src/agents/hydrologist.py` — changes=7, cumulative_share=0.2152 [static-analysis]
- `src/agents/surveyor.py` — changes=6, cumulative_share=0.2911 [static-analysis]
- `pyproject.toml` — changes=6, cumulative_share=0.3671 [static-analysis]
- `src/cli.py` — changes=6, cumulative_share=0.443 [static-analysis]
- `src/agents/semanticist.py` — changes=5, cumulative_share=0.5063 [static-analysis]
- `src/orchestrator.py` — changes=5, cumulative_share=0.5696 [static-analysis]
- `src/agents/navigator.py` — changes=4, cumulative_share=0.6203 [static-analysis]
- `src/analyzers/tree_sitter_analyzer.py` — changes=3, cumulative_share=0.6582 [static-analysis]
- `src/agents/archivist.py` — changes=3, cumulative_share=0.6962 [static-analysis]
- `src/agents/__init__.py` — changes=3, cumulative_share=0.7342 [static-analysis]
- `src/graph/knowledge_graph.py` — changes=3, cumulative_share=0.7722 [static-analysis]
- `tests/test_agents.py` — changes=2, cumulative_share=0.7975 [static-analysis]
- `src/models/__init__.py` — changes=2, cumulative_share=0.8228 [static-analysis]

## Module Purpose Index
- `dashboard/src/app/api/cartography/route.ts` [domain=serving-2] — This module supports the codebase by owning line:import { NextResponse } from "next/server";, line:import fs from "fs";, line:import path from "path";. Its business value is enabling consistent system behavior for the capability represented by route. [method=llm-inference]
- `dashboard/src/components/OverviewCards.tsx` [domain=serving-1] — This module supports the codebase by owning line:"use client";, line:import type { CartographyData } from "@/lib/types";, line:interface Props { data: CartographyData; }. Its business value is enabling consistent system behavior for the capability represented by OverviewCards. [method=llm-inference]
- `dashboard/src/lib/types.ts` [domain=serving-1] — This module supports the codebase by owning line:export interface GraphNode {, line:id: string;, line:node_type?: string;. Its business value is enabling consistent system behavior for the capability represented by types. [method=llm-inference]
- `src/agents/hydrologist.py` [domain=analysis-1] — This module supports the codebase by owning import_from:__future__, import:json, import_from:pathlib. Its business value is enabling consistent system behavior for the capability represented by hydrologist. [method=llm-inference]
- `src/agents/semanticist.py` [domain=analysis-1] — This module supports the codebase by owning import_from:__future__, import:ast, import:json. Its business value is enabling consistent system behavior for the capability represented by semanticist. [method=llm-inference]
- `src/agents/surveyor.py` [domain=analysis-2] — This module supports the codebase by owning import_from:__future__, import:subprocess, import_from:collections. Its business value is enabling consistent system behavior for the capability represented by surveyor. [method=llm-inference]
- `src/analyzers/tree_sitter_analyzer.py` [domain=analysis-1] — This module supports the codebase by owning import_from:__future__, import:ast, import_from:pathlib. Its business value is enabling consistent system behavior for the capability represented by tree_sitter_analyzer. [method=llm-inference]
- `src/orchestrator.py` [domain=orchestration] — This module supports the codebase by owning import_from:__future__, import:json, import:shutil. Its business value is enabling consistent system behavior for the capability represented by orchestrator. [method=llm-inference]
