# CODEBASE: Living Context

## Architecture Overview
This repository is organized as an analysis-focused architecture where static structure (39 modules, 42 import edges) is combined with data lineage (0 datasets, 0 lineage edges) and semantic domain inference (7 inferred domains) to provide operational intelligence for maintenance, risk assessment, and onboarding.

## Critical Path (Top 5 by PageRank)
1. `src/tracing.py` — PageRank `0.1092` [static-analysis]
2. `src/models/lineage.py` — PageRank `0.0683` [static-analysis]
3. `src/models/graph.py` — PageRank `0.0560` [static-analysis]
4. `src/models/module.py` — PageRank `0.0532` [static-analysis]
5. `src/agents/navigator.py` — PageRank `0.0395` [static-analysis]

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
- `README.md` — changes=10, cumulative_share=0.1351 [static-analysis]
- `pyproject.toml` — changes=6, cumulative_share=0.2162 [static-analysis]
- `src/agents/hydrologist.py` — changes=6, cumulative_share=0.2973 [static-analysis]
- `src/cli.py` — changes=6, cumulative_share=0.3784 [static-analysis]
- `src/agents/surveyor.py` — changes=5, cumulative_share=0.4459 [static-analysis]
- `src/agents/navigator.py` — changes=4, cumulative_share=0.5 [static-analysis]
- `src/orchestrator.py` — changes=4, cumulative_share=0.5541 [static-analysis]
- `src/agents/semanticist.py` — changes=4, cumulative_share=0.6081 [static-analysis]
- `src/agents/archivist.py` — changes=3, cumulative_share=0.6486 [static-analysis]
- `src/agents/__init__.py` — changes=3, cumulative_share=0.6892 [static-analysis]
- `src/graph/knowledge_graph.py` — changes=3, cumulative_share=0.7297 [static-analysis]
- `tests/test_agents.py` — changes=2, cumulative_share=0.7568 [static-analysis]
- `src/analyzers/tree_sitter_analyzer.py` — changes=2, cumulative_share=0.7838 [static-analysis]
- `src/models/__init__.py` — changes=2, cumulative_share=0.8108 [static-analysis]

## Module Purpose Index
- `dashboard/AGENTS.md` [domain=analysis-1] — This module supports the codebase by owning line:<!-- BEGIN:nextjs-agent-rules -->, line:# This is NOT the Next.js you know, line:This version has breaking changes — APIs, conventions, and file structure may al. Its business value is enabling consistent system behavior for the capability represented by AGENTS. [method=llm-inference]
- `dashboard/CLAUDE.md` [domain=analysis-1] — This module supports the codebase by owning line:@AGENTS.md, file:CLAUDE.md. Its business value is enabling consistent system behavior for the capability represented by CLAUDE. [method=llm-inference]
- `dashboard/next-env.d.ts` [domain=ingestion-1] — This module supports the codebase by owning line:/// <reference types="next" />, line:/// <reference types="next/image-types/global" />, line:import "./.next/dev/types/routes.d.ts";. Its business value is enabling consistent system behavior for the capability represented by next-env.d. [method=llm-inference]
- `dashboard/next.config.ts` [domain=ingestion-1] — This module supports the codebase by owning line:import type { NextConfig } from "next";, line:const nextConfig: NextConfig = {, line:/* config options here */. Its business value is enabling consistent system behavior for the capability represented by next.config. [method=llm-inference]
- `dashboard/README.md` [domain=ingestion-1] — This module supports the codebase by owning line:This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-, line:## Getting Started, line:First, run the development server:. Its business value is enabling consistent system behavior for the capability represented by README. [method=llm-inference]
- `dashboard/src/app/api/cartography/route.ts` [domain=ingestion-1] — This module supports the codebase by owning line:import { NextResponse } from "next/server";, line:import fs from "fs";, line:import path from "path";. Its business value is enabling consistent system behavior for the capability represented by route. [method=llm-inference]
- `dashboard/src/app/api/query/route.ts` [domain=ingestion-1] — This module supports the codebase by owning line:import { NextRequest, NextResponse } from "next/server";, line:import { exec } from "child_process";, line:import path from "path";. Its business value is enabling consistent system behavior for the capability represented by route. [method=llm-inference]
- `dashboard/src/app/layout.tsx` [domain=ingestion-1] — This module supports the codebase by owning line:import type { Metadata } from "next";, line:import { Geist_Mono } from "next/font/google";, line:import "./globals.css";. Its business value is enabling consistent system behavior for the capability represented by layout. [method=llm-inference]
- `dashboard/src/app/page.tsx` [domain=ingestion-2] — This module supports the codebase by owning line:"use client";, line:import { useCartographyData } from "@/lib/hooks";, line:import { OverviewCards } from "@/components/OverviewCards";. Its business value is enabling consistent system behavior for the capability represented by page. [method=llm-inference]
- `dashboard/src/components/DomainChart.tsx` [domain=ingestion-2] — This module supports the codebase by owning line:"use client";, line:import {, line:PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend,. Its business value is enabling consistent system behavior for the capability represented by DomainChart. [method=llm-inference]
- `dashboard/src/components/FDEAnswers.tsx` [domain=ingestion-2] — This module supports the codebase by owning line:"use client";, line:import type { FDEAnswers as FDEAnswersType } from "@/lib/types";, line:interface Props { answers: FDEAnswersType | null; }. Its business value is enabling consistent system behavior for the capability represented by FDEAnswers. [method=llm-inference]
- `dashboard/src/components/ModuleGraph.tsx` [domain=ingestion-2] — This module supports the codebase by owning line:"use client";, line:import { useMemo } from "react";, line:import ReactFlow, {. Its business value is enabling consistent system behavior for the capability represented by ModuleGraph. [method=llm-inference]
- `dashboard/src/components/ModuleTable.tsx` [domain=ingestion-2] — This module supports the codebase by owning line:"use client";, line:import { useState } from "react";, line:import type { ModulePurpose } from "@/lib/types";. Its business value is enabling consistent system behavior for the capability represented by ModuleTable. [method=llm-inference]
- `dashboard/src/components/NavBar.tsx` [domain=ingestion-2] — This module supports the codebase by owning line:"use client";, line:export function NavBar() {, line:const links = [. Its business value is enabling consistent system behavior for the capability represented by NavBar. [method=llm-inference]
- `dashboard/src/components/OverviewCards.tsx` [domain=ingestion-2] — This module supports the codebase by owning line:"use client";, line:import type { CartographyData } from "@/lib/types";, line:interface Props { data: CartographyData; }. Its business value is enabling consistent system behavior for the capability represented by OverviewCards. [method=llm-inference]
- `dashboard/src/components/QueryPanel.tsx` [domain=ingestion-2] — This module supports the codebase by owning line:"use client";, line:import { useState } from "react";, line:const EXAMPLES = [. Its business value is enabling consistent system behavior for the capability represented by QueryPanel. [method=llm-inference]
- `dashboard/src/components/TraceLog.tsx` [domain=ingestion-2] — This module supports the codebase by owning line:"use client";, line:import { Fragment, useState } from "react";, line:import type { TraceEntry } from "@/lib/types";. Its business value is enabling consistent system behavior for the capability represented by TraceLog. [method=llm-inference]
- `dashboard/src/lib/hooks.ts` [domain=ingestion-2] — This module supports the codebase by owning line:"use client";, line:import { useEffect, useState } from "react";, line:import type { CartographyData } from "./types";. Its business value is enabling consistent system behavior for the capability represented by hooks. [method=llm-inference]
- `dashboard/src/lib/types.ts` [domain=ingestion-2] — This module supports the codebase by owning line:export interface GraphNode {, line:id: string;, line:node_type?: string;. Its business value is enabling consistent system behavior for the capability represented by types. [method=llm-inference]
- `main.py` [domain=transformation-2] — This module supports the codebase by owning import_from:src.cli, file:main.py. Its business value is enabling consistent system behavior for the capability represented by main. [method=llm-inference]
- `README.md` [domain=ingestion-2] — This module supports the codebase by owning line:# TRP1 Week 4: Brownfield Cartographer, line:A multi-agent codebase intelligence system that ingests any GitHub repository or, line:## Quick Start. Its business value is enabling consistent system behavior for the capability represented by README. [method=llm-inference]
- `RECONNAISSANCE.md` [domain=transformation-1] — This module supports the codebase by owning line:# RECONNAISSANCE: dbt-labs/jaffle-shop (classic), line:Target repo: https://github.com/dbt-labs/jaffle-shop-classic (redirected from ht, line:This is a small, self-contained dbt project that models a fictional e‑commerce s. Its business value is enabling consistent system behavior for the capability represented by RECONNAISSANCE. [method=llm-inference]
- `src/__init__.py` [domain=ingestion-2] — This module supports the codebase by owning line:"""Brownfield Cartographer source package.""", file:__init__.py. Its business value is enabling consistent system behavior for the capability represented by __init__. [method=llm-inference]
- `src/agents/__init__.py` [domain=analysis-2] — This module supports the codebase by owning import_from:src.agents.archivist, import_from:src.agents.hydrologist, import_from:src.agents.navigator. Its business value is enabling consistent system behavior for the capability represented by __init__. [method=llm-inference]
- `src/agents/archivist.py` [domain=transformation-2] — This module supports the codebase by owning import_from:__future__, import_from:pathlib, import_from:src.tracing. Its business value is enabling consistent system behavior for the capability represented by archivist. [method=llm-inference]
- `src/agents/hydrologist.py` [domain=transformation-2] — This module supports the codebase by owning import_from:__future__, import:json, import_from:pathlib. Its business value is enabling consistent system behavior for the capability represented by hydrologist. [method=llm-inference]
- `src/agents/navigator.py` [domain=analysis-2] — This module supports the codebase by owning import_from:__future__, import:json, import:re. Its business value is enabling consistent system behavior for the capability represented by navigator. [method=llm-inference]
- `src/agents/semanticist.py` [domain=analysis-2] — This module supports the codebase by owning import_from:__future__, import:ast, import:json. Its business value is enabling consistent system behavior for the capability represented by semanticist. [method=llm-inference]
- `src/agents/surveyor.py` [domain=analysis-2] — This module supports the codebase by owning import_from:__future__, import:subprocess, import_from:collections. Its business value is enabling consistent system behavior for the capability represented by surveyor. [method=llm-inference]
- `src/analyzers/dag_config_parser.py` [domain=transformation-2] — This module supports the codebase by owning import_from:__future__, import_from:pathlib, import:yaml. Its business value is enabling consistent system behavior for the capability represented by dag_config_parser. [method=llm-inference]
- `src/analyzers/python_dataflow.py` [domain=transformation-2] — This module supports the codebase by owning import_from:__future__, import:ast, import_from:pathlib. Its business value is enabling consistent system behavior for the capability represented by python_dataflow. [method=llm-inference]
- `src/analyzers/sql_lineage.py` [domain=transformation-2] — This module supports the codebase by owning import_from:__future__, import:re, import_from:pathlib. Its business value is enabling consistent system behavior for the capability represented by sql_lineage. [method=llm-inference]
- `src/analyzers/tree_sitter_analyzer.py` [domain=transformation-2] — This module supports the codebase by owning import_from:__future__, import:ast, import_from:pathlib. Its business value is enabling consistent system behavior for the capability represented by tree_sitter_analyzer. [method=llm-inference]
- `src/cli.py` [domain=transformation-2] — This module supports the codebase by owning import_from:__future__, import:argparse, import_from:pathlib. Its business value is enabling consistent system behavior for the capability represented by cli. [method=llm-inference]
- `src/graph/__init__.py` [domain=transformation-2] — This module supports the codebase by owning line:"""Knowledge graph utilities.""", file:__init__.py. Its business value is enabling consistent system behavior for the capability represented by __init__. [method=llm-inference]
- `src/graph/knowledge_graph.py` [domain=transformation-2] — This module supports the codebase by owning import_from:__future__, import:json, import_from:pathlib. Its business value is enabling consistent system behavior for the capability represented by knowledge_graph. [method=llm-inference]
- `src/models/__init__.py` [domain=transformation-2] — This module supports the codebase by owning import_from:src.models.graph, import_from:src.models.lineage, import_from:src.models.module. Its business value is enabling consistent system behavior for the capability represented by __init__. [method=llm-inference]
- `src/models/graph.py` [domain=transformation-2] — This module supports the codebase by owning import_from:__future__, import_from:datetime, import_from:typing. Its business value is enabling consistent system behavior for the capability represented by graph. [method=llm-inference]
- `src/models/lineage.py` [domain=transformation-2] — This module supports the codebase by owning import_from:__future__, import_from:pydantic, class:TransformationEvent. Its business value is enabling consistent system behavior for the capability represented by lineage. [method=llm-inference]
- `src/models/module.py` [domain=transformation-2] — This module supports the codebase by owning import_from:__future__, import_from:pydantic, class:FunctionInfo. Its business value is enabling consistent system behavior for the capability represented by module. [method=llm-inference]
- `src/orchestrator.py` [domain=transformation-2] — This module supports the codebase by owning import_from:__future__, import:json, import:shutil. Its business value is enabling consistent system behavior for the capability represented by orchestrator. [method=llm-inference]
- `src/tracing.py` [domain=transformation-2] — This module supports the codebase by owning import_from:__future__, import:json, import_from:dataclasses. Its business value is enabling consistent system behavior for the capability represented by tracing. [method=llm-inference]
- `tests/test_agents.py` [domain=serving] — This module supports the codebase by owning import_from:__future__, import:json, import:tempfile. Its business value is enabling consistent system behavior for the capability represented by test_agents. [method=llm-inference]
- `tests/test_knowledge_graph_deserialization.py` [domain=serving] — This module supports the codebase by owning import_from:__future__, import:json, import:tempfile. Its business value is enabling consistent system behavior for the capability represented by test_knowledge_graph_deserialization. [method=llm-inference]
