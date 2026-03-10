# Brownfield Cartographer (Phase 1 + Phase 2)

This repository now implements:

- **Phase 1: Surveyor Agent (Static Structure)**
- **Phase 2: Hydrologist Agent (Data Lineage)**

## What is implemented

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

## Run

Install dependencies, then run analysis on any local repo path.

- `python main.py analyze .`
- `python main.py analyze /path/to/repo --days 90`

You can also use the script entrypoint:

- `cartographer analyze .`

## Output

- `.cartography/module_graph.json`
- `.cartography/lineage_graph.json`

