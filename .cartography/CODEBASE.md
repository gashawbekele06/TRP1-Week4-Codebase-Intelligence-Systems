# CODEBASE: Living Context

## Architecture Overview
This repository is organized as an analysis-focused architecture where static structure (15 modules, 0 import edges) is combined with data lineage (0 datasets, 0 lineage edges) and semantic domain inference (5 inferred domains) to provide operational intelligence for maintenance, risk assessment, and onboarding.

## Critical Path (Top 5 by PageRank)
1. `dashboard\next.config.ts` — PageRank `0.0667` [static-analysis]
2. `dashboard\src\app\api\cartography\route.ts` — PageRank `0.0667` [static-analysis]
3. `dashboard\src\app\api\query\route.ts` — PageRank `0.0667` [static-analysis]
4. `dashboard\src\app\layout.tsx` — PageRank `0.0667` [static-analysis]
5. `dashboard\src\app\page.tsx` — PageRank `0.0667` [static-analysis]

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
- `README.md` — changes=10, cumulative_share=0.0481 [static-analysis]
- `.cartography/module_graph.json` — changes=8, cumulative_share=0.0865 [static-analysis]
- `pyproject.toml` — changes=6, cumulative_share=0.1154 [static-analysis]
- `src/agents/hydrologist.py` — changes=6, cumulative_share=0.1442 [static-analysis]
- `src/cli.py` — changes=6, cumulative_share=0.1731 [static-analysis]
- `.cartography/CODEBASE.md` — changes=5, cumulative_share=0.1971 [static-analysis]
- `.cartography/cartography_trace.jsonl` — changes=5, cumulative_share=0.2212 [static-analysis]
- `.cartography/run_state.json` — changes=5, cumulative_share=0.2452 [static-analysis]
- `.cartography/semantic_report.json` — changes=5, cumulative_share=0.2692 [static-analysis]
- `src/agents/surveyor.py` — changes=5, cumulative_share=0.2933 [static-analysis]
- `.cartography/onboarding_brief.md` — changes=4, cumulative_share=0.3125 [static-analysis]
- `src/agents/navigator.py` — changes=4, cumulative_share=0.3317 [static-analysis]
- `.cartography/lineage_graph.json` — changes=4, cumulative_share=0.351 [static-analysis]
- `src/orchestrator.py` — changes=4, cumulative_share=0.3702 [static-analysis]
- `src/graph/__pycache__/knowledge_graph.cpython-313.pyc` — changes=4, cumulative_share=0.3894 [static-analysis]
- `src/agents/__pycache__/hydrologist.cpython-313.pyc` — changes=4, cumulative_share=0.4087 [static-analysis]
- `src/agents/__pycache__/surveyor.cpython-313.pyc` — changes=4, cumulative_share=0.4279 [static-analysis]
- `src/agents/semanticist.py` — changes=4, cumulative_share=0.4471 [static-analysis]
- `src/__pycache__/cli.cpython-313.pyc` — changes=4, cumulative_share=0.4663 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/PKG-INFO` — changes=3, cumulative_share=0.4808 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/SOURCES.txt` — changes=3, cumulative_share=0.4952 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/requires.txt` — changes=3, cumulative_share=0.5096 [static-analysis]
- `src/agents/archivist.py` — changes=3, cumulative_share=0.524 [static-analysis]
- `src/models/__pycache__/__init__.cpython-313.pyc` — changes=3, cumulative_share=0.5385 [static-analysis]
- `src/agents/__pycache__/__init__.cpython-313.pyc` — changes=3, cumulative_share=0.5529 [static-analysis]
- `src/agents/__init__.py` — changes=3, cumulative_share=0.5673 [static-analysis]
- `src/graph/knowledge_graph.py` — changes=3, cumulative_share=0.5817 [static-analysis]
- `src/analyzers/__pycache__/python_dataflow.cpython-313.pyc` — changes=3, cumulative_share=0.5962 [static-analysis]
- `src/analyzers/__pycache__/tree_sitter_analyzer.cpython-313.pyc` — changes=3, cumulative_share=0.6106 [static-analysis]
- `dashboard/src/components/DomainChart.tsx` — changes=2, cumulative_share=0.6202 [static-analysis]
- `dashboard/src/components/TraceLog.tsx` — changes=2, cumulative_share=0.6298 [static-analysis]
- `tests/test_agents.py` — changes=2, cumulative_share=0.6394 [static-analysis]
- `uv.lock` — changes=2, cumulative_share=0.649 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/dependency_links.txt` — changes=2, cumulative_share=0.6587 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/entry_points.txt` — changes=2, cumulative_share=0.6683 [static-analysis]
- `src/trp1_week3_codebase_intelligence_systems.egg-info/top_level.txt` — changes=2, cumulative_share=0.6779 [static-analysis]
- `.cartography/navigator_agent.json` — changes=2, cumulative_share=0.6875 [static-analysis]
- `src/models/__pycache__/graph.cpython-313.pyc` — changes=2, cumulative_share=0.6971 [static-analysis]
- `src/models/__pycache__/lineage.cpython-313.pyc` — changes=2, cumulative_share=0.7067 [static-analysis]
- `src/models/__pycache__/module.cpython-313.pyc` — changes=2, cumulative_share=0.7163 [static-analysis]
- `src/graph/__pycache__/__init__.cpython-313.pyc` — changes=2, cumulative_share=0.726 [static-analysis]
- `src/__pycache__/__init__.cpython-313.pyc` — changes=2, cumulative_share=0.7356 [static-analysis]
- `src/__pycache__/orchestrator.cpython-313.pyc` — changes=2, cumulative_share=0.7452 [static-analysis]
- `src/analyzers/__pycache__/dag_config_parser.cpython-313.pyc` — changes=2, cumulative_share=0.7548 [static-analysis]
- `src/analyzers/__pycache__/sql_lineage.cpython-313.pyc` — changes=2, cumulative_share=0.7644 [static-analysis]
- `src/analyzers/tree_sitter_analyzer.py` — changes=2, cumulative_share=0.774 [static-analysis]
- `src/models/__init__.py` — changes=2, cumulative_share=0.7837 [static-analysis]
- `src/analyzers/python_dataflow.py` — changes=2, cumulative_share=0.7933 [static-analysis]
- `main.py` — changes=2, cumulative_share=0.8029 [static-analysis]

## Module Purpose Index
- `dashboard/AGENTS.md` [domain=analysis] — This module supports the codebase by owning line:<!-- BEGIN:nextjs-agent-rules -->, line:# This is NOT the Next.js you know, line:This version has breaking changes — APIs, conventions, and file structure may al. Its business value is enabling consistent system behavior for the capability represented by AGENTS. [method=llm-inference]
- `dashboard/CLAUDE.md` [domain=analysis] — This module supports the codebase by owning line:@AGENTS.md, file:CLAUDE.md. Its business value is enabling consistent system behavior for the capability represented by CLAUDE. [method=llm-inference]
- `dashboard/next.config.ts` [domain=ingestion] — This module supports the codebase by owning line:import type { NextConfig } from "next";, line:const nextConfig: NextConfig = {, line:/* config options here */. Its business value is enabling consistent system behavior for the capability represented by next.config. [method=llm-inference]
- `dashboard/README.md` [domain=ingestion] — This module supports the codebase by owning line:This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-, line:## Getting Started, line:First, run the development server:. Its business value is enabling consistent system behavior for the capability represented by README. [method=llm-inference]
- `dashboard/src/app/api/cartography/route.ts` [domain=ingestion] — This module supports the codebase by owning line:import { NextResponse } from "next/server";, line:import fs from "fs";, line:import path from "path";. Its business value is enabling consistent system behavior for the capability represented by route. [method=llm-inference]
- `dashboard/src/app/api/query/route.ts` [domain=ingestion] — This module supports the codebase by owning line:import { NextRequest, NextResponse } from "next/server";, line:import { exec } from "child_process";, line:import path from "path";. Its business value is enabling consistent system behavior for the capability represented by route. [method=llm-inference]
- `dashboard/src/app/layout.tsx` [domain=ingestion] — This module supports the codebase by owning line:import type { Metadata } from "next";, line:import { Geist_Mono } from "next/font/google";, line:import "./globals.css";. Its business value is enabling consistent system behavior for the capability represented by layout. [method=llm-inference]
- `dashboard/src/app/page.tsx` [domain=ingestion] — This module supports the codebase by owning line:"use client";, line:import { useCartographyData } from "@/lib/hooks";, line:import { OverviewCards } from "@/components/OverviewCards";. Its business value is enabling consistent system behavior for the capability represented by page. [method=llm-inference]
- `dashboard/src/components/DomainChart.tsx` [domain=serving] — This module supports the codebase by owning line:"use client";, line:import {, line:PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend,. Its business value is enabling consistent system behavior for the capability represented by DomainChart. [method=llm-inference]
- `dashboard/src/components/FDEAnswers.tsx` [domain=serving] — This module supports the codebase by owning line:"use client";, line:import type { FDEAnswers as FDEAnswersType } from "@/lib/types";, line:interface Props { answers: FDEAnswersType | null; }. Its business value is enabling consistent system behavior for the capability represented by FDEAnswers. [method=llm-inference]
- `dashboard/src/components/ModuleGraph.tsx` [domain=serving] — This module supports the codebase by owning line:"use client";, line:import { useMemo } from "react";, line:import ReactFlow, {. Its business value is enabling consistent system behavior for the capability represented by ModuleGraph. [method=llm-inference]
- `dashboard/src/components/ModuleTable.tsx` [domain=serving] — This module supports the codebase by owning line:"use client";, line:import { useState } from "react";, line:import type { ModulePurpose } from "@/lib/types";. Its business value is enabling consistent system behavior for the capability represented by ModuleTable. [method=llm-inference]
- `dashboard/src/components/NavBar.tsx` [domain=analysis] — This module supports the codebase by owning line:"use client";, line:export function NavBar() {, line:const links = [. Its business value is enabling consistent system behavior for the capability represented by NavBar. [method=llm-inference]
- `dashboard/src/components/OverviewCards.tsx` [domain=serving] — This module supports the codebase by owning line:"use client";, line:import type { CartographyData } from "@/lib/types";, line:interface Props { data: CartographyData; }. Its business value is enabling consistent system behavior for the capability represented by OverviewCards. [method=llm-inference]
- `dashboard/src/components/QueryPanel.tsx` [domain=analysis] — This module supports the codebase by owning line:"use client";, line:import { useState } from "react";, line:const EXAMPLES = [. Its business value is enabling consistent system behavior for the capability represented by QueryPanel. [method=llm-inference]
- `dashboard/src/components/TraceLog.tsx` [domain=serving] — This module supports the codebase by owning line:"use client";, line:import { Fragment, useState } from "react";, line:import type { TraceEntry } from "@/lib/types";. Its business value is enabling consistent system behavior for the capability represented by TraceLog. [method=llm-inference]
- `dashboard/src/lib/hooks.ts` [domain=serving] — This module supports the codebase by owning line:"use client";, line:import { useEffect, useState } from "react";, line:import type { CartographyData } from "./types";. Its business value is enabling consistent system behavior for the capability represented by hooks. [method=llm-inference]
- `dashboard/src/lib/types.ts` [domain=serving] — This module supports the codebase by owning line:export interface GraphNode {, line:id: string;, line:node_type?: string;. Its business value is enabling consistent system behavior for the capability represented by types. [method=llm-inference]
