# Brownfield Cartographer (Phase 1)

This repository now implements **Phase 1: Surveyor Agent (Static Structure)**.

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

## Run

Install dependencies, then run analysis on any local repo path.

- `python main.py analyze .`
- `python main.py analyze /path/to/repo --days 90`

You can also use the script entrypoint:

- `cartographer analyze .`

## Output

- `.cartography/module_graph.json`

