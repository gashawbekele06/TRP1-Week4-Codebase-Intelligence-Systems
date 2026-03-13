# Brownfield Cartographer (Phase 1 + Phase 2 + Phase 3 + Phase 4)

This repository now implements:

- **Phase 1: Surveyor Agent (Static Structure)**
- **Phase 2: Hydrologist Agent (Data Lineage)**
- **Phase 3: Semanticist Agent (LLM-Powered Purpose Analyst)**
- **Phase 4: Archivist + Navigator (Living Context + Query Interface)**
- **Orchestrator** to run Surveyor -> Hydrologist -> Semanticist -> Archivist in sequence

## What is implemented

### Phase 1 (Surveyor)

- Tree-sitter language routing for:
	- Python (`.py`)
	- SQL (`.sql`)
	- YAML (`.yml`, `.yaml`)
	- JavaScript/TypeScript (`.js`, `.jsx`, `.ts`, `.tsx`)
- `analyze_module(path)` for Python modules:
	- Import extraction (including relative import resolution)
	- Public function extraction (leading underscores stripped into `normalized_name`)
	- Class extraction with inheritance information
- Git velocity extraction over rolling window (`--days`, default 30)
- High-velocity core detection (top ~20% files explaining ~80% changes)
- Module import graph with:
	- PageRank hubs
	- Strongly connected components (circular dependencies)
- Dead code candidate detection for exported Python symbols with no references
- Graph serialization to `.cartography/module_graph.json`

### Phase 2 (Hydrologist)

- Python data flow extraction for:
	- pandas: `read_csv`, `read_sql`
	- SQLAlchemy: `execute(...)`
	- PySpark: common read/write paths (`read.csv/json/parquet/orc/table/load`, `write.*`, `saveAsTable`)
- Dynamic string handling:
	- f-strings / variable references are flagged as `dynamic reference, cannot resolve`
- SQL lineage via `sqlglot` with dialect fallback:
	- PostgreSQL, BigQuery, Snowflake, DuckDB
	- Handles dbt `ref()` and `source()` normalization
- YAML DAG/config topology extraction:
	- dbt `schema.yml` model/source structures
	- generic YAML `tasks` + `upstream` relationships
- Unified `DataLineageGraph` (NetworkX DiGraph) with:
	- `blast_radius(node)` downstream traversal support in agent
	- `find_sources()` and `find_sinks()`
- Graph serialization to `.cartography/lineage_graph.json`

### Phase 3 (Semanticist)

- Per-module **Purpose Statement** generation based on implementation evidence
	(not module docstrings).
- Documentation Drift detection:
	- flags modules whose docstring intent appears inconsistent with implementation evidence.
- Business Domain boundary inference:
	- embeds all purpose statements and performs k-means clustering to produce a Domain Architecture Map
	- target cluster range is 5-8 where module count supports it.
- Five FDE Day-One answer synthesis:
	- combines Surveyor + Hydrologist outputs with semantic reasoning over the repository context.
	- includes evidence citations (`file_path:line-range`) in synthesized answers.
- Cost discipline:
	- fast/cheap model (Gemini Flash) for bulk module extraction
	- higher-capability model (Claude/GPT-4 tier) reserved for final synthesis only
	- ContextWindowBudget enforces pre-call token/spend admission checks and tracks cumulative estimated + actual usage.
	- graceful heuristic fallback if no API key is configured.

### Phase 4 (Archivist + Navigator)

- `generate_CODEBASE_md()` produces `.cartography/CODEBASE.md` with:
	- Architecture Overview
	- Critical Path (top 5 by PageRank)
	- Data Sources & Sinks
	- Known Debt (circular dependencies + documentation drift)
	- High-Velocity Files
- 	- Module Purpose Index (from Semanticist purpose statements)
- Archivist also produces `.cartography/onboarding_brief.md` for day-one onboarding,
	including explicit answers to the five FDE Day-One questions.
- Navigator query agent (`query` command):
	- built with LangGraph workflow when available, deterministic fallback otherwise
	- uses 4 tools:
		- `find_implementation(concept)`
		- `trace_lineage(dataset, direction)`
		- `blast_radius(module_path)`
		- `explain_module(path)`
	- enforces citations containing file, line range, and analysis method attribution
		(`static-analysis` vs `llm-inference`)
- Audit trail:
	- `.cartography/cartography_trace.jsonl` logs every major agent action,
		evidence source, confidence score, and metadata.
- Incremental update mode:
	- detects new commits since last run via git commit state
	- re-analyzes only changed files when available
	- persists state in `.cartography/run_state.json`

## Run

Install dependencies, then run analysis on any local repo path or GitHub URL.

- `python main.py analyze .`
- `python main.py analyze /path/to/repo --days 90`
- `python main.py analyze https://github.com/dbt-labs/jaffle-shop --days 90`
- `python main.py query "What is the riskiest module and why?"`
- `python main.py query` (interactive mode)

You can also use the script entrypoint:

- `cartographer analyze .`
- `cartographer query "Where is business logic concentrated?"`
- `cartographer query` (interactive mode)

Backward-compatible alias:

- `ask` still works as an alias for `query`.

### Optional LLM configuration

Create or edit `.env` in the repository root:

- `OPENROUTER_API_KEY=<your key>`
- `OPENROUTER_FAST_MODEL=google/gemini-2.0-flash-001`
- `OPENROUTER_SYNTHESIS_MODEL=anthropic/claude-3.5-sonnet`
- `SEMANTICIST_MAX_TOKENS=120000`
- `SEMANTICIST_MAX_SPEND_USD=5.0`

If `OPENROUTER_API_KEY` is missing, Semanticist runs in heuristic mode and records warnings.

## Output

- `.cartography/module_graph.json`
- `.cartography/lineage_graph.json`
- `.cartography/semantic_report.json`
- `.cartography/CODEBASE.md`
- `.cartography/onboarding_brief.md`
- `.cartography/cartography_trace.jsonl`
- `.cartography/run_state.json`
- `.cartography/navigator_agent.json`

## Key files

- `src/orchestrator.py`: Analysis orchestration and GitHub URL ingestion
- `src/agents/semanticist.py`: Semantic purpose extraction, domain inference, and FDE synthesis
- `src/agents/archivist.py`: Living context generation (`CODEBASE.md`) + onboarding brief
- `src/agents/navigator.py`: Query interface with citation-backed responses
- `src/tracing.py`: JSONL trace/audit logging utility

