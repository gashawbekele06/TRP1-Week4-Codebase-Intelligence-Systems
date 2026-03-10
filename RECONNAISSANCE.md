# RECONNAISSANCE: dbt-labs/jaffle-shop (classic)

Target repo: https://github.com/dbt-labs/jaffle-shop-classic (redirected from https://github.com/dbt-labs/jaffle-shop at time of analysis).

This is a small, self-contained dbt project that models a fictional e‑commerce store ("jaffle_shop"). It consists of:
- `seeds/`: three CSVs (`raw_customers.csv`, `raw_orders.csv`, `raw_payments.csv`) plus a `.gitkeep`.
- `models/staging/`: three staging models (`stg_customers.sql`, `stg_orders.sql`, `stg_payments.sql`) and `schema.yml`.
- `models/`: mart-level models (`customers.sql`, `orders.sql`), documentation files (`docs.md`, `overview.md`), and `schema.yml`.
- `dbt_project.yml`: dbt project configuration.

The README describes this as a simple playground dbt project that transforms raw app data into analytics-ready `customers` and `orders` tables.

---

## The Five FDE Day-One Questions (Manual Answers)

### 1. What is the primary data ingestion path?

In this project, "ingestion" is implemented via dbt **seeds**, not external sources:

1. The raw data lives in CSVs under `seeds/`:
   - `seeds/raw_customers.csv`
   - `seeds/raw_orders.csv`
   - `seeds/raw_payments.csv`
2. Running `dbt seed` loads these CSVs into the target warehouse as raw tables (one per CSV) in the `jaffle_shop` schema.
3. The staging models in `models/staging/` (`stg_customers`, `stg_orders`, `stg_payments`) select from those seeded tables, cleaning and standardizing the raw data.
4. The final mart models in `models/` (`customers`, `orders`) build analytics-ready tables on top of the staging layer.

So the primary ingestion path is:

> **Local CSVs → `dbt seed` → raw warehouse tables → staging models → final marts.**

There is no upstream streaming or ELT tool shown in this repo; it assumes the CSVs are the source of truth for raw data.

---

### 2. What are the 3–5 most critical output datasets/endpoints?

Given the size and intent of the project, the critical outputs are the analytics-ready dbt models that an analyst would actually query:

1. **`models/customers.sql` → `customers` table**  
   - Customer-level grain, derived from `stg_customers` and (likely) order/payment rollups.  
   - Represents the single place to go for customer attributes and lifetime metrics.

2. **`models/orders.sql` → `orders` table**  
   - Order-level fact table that joins staged orders and payments.  
   - Central for revenue, order volume, and payment status metrics.

3. **Staging models as critical intermediates:**  
   - `models/staging/stg_customers.sql`  
   - `models/staging/stg_orders.sql`  
   - `models/staging/stg_payments.sql`  
   These are not usually queried directly, but they are the only bridge between the raw seeded tables and the marts. If they are wrong, every downstream model is wrong.

In practice, for downstream consumers, `customers` and `orders` are the 2 key output datasets; the staging models are structurally critical even if not user-facing.

---

### 3. What is the blast radius if the most critical module fails?

Taking **`models/orders.sql`** as the most critical module (central fact table):

- If `orders` fails to build (syntax error, schema change, or bad logic):
  - Any analytics or dashboards that read from the `orders` table will either fail or return stale data.
  - Tests defined in `models/schema.yml` that reference `orders` would fail, blocking CI-style checks if present.
  - Any downstream models that might depend on `orders` (e.g., customer-level aggregates in `customers`) would fail to build or produce incorrect results.
- Even if the model runs but its logic is wrong (e.g., mis-joining payments or misclassifying order status), then:
  - Revenue, order count, and payment-status metrics derived from `orders` become untrustworthy.

Overall blast radius: **medium-to-high for this repo**—most interesting business questions ("how many orders? how much revenue? what’s the payment success rate?") run through `orders`, and the `customers` model likely depends on it for lifetime metrics.

---

### 4. Where is the business logic concentrated vs. distributed?

In this dbt project, business logic is **highly concentrated** in a small number of SQL models:

- **Concentrated:**
  - `models/staging/` layer: cleaning, renaming, basic transformations of raw customers, orders, and payments. This encodes assumptions about keys, timestamps, status fields, and how to interpret "raw" data from the app.
  - `models/customers.sql` and `models/orders.sql`: higher-level logic that defines what an order is, how payments are associated, and what constitutes customer-level metrics. This is where business questions (e.g., "what is a customer?", "what is an order?", "what counts as revenue?") get formalized.

- **Not widely distributed:**
  - There are no macros, packages, or separate Python services in this repo.  
  - Configuration and documentation live in a few `schema.yml` and markdown files, but they mostly describe rather than implement logic.

So for an FDE trying to understand "how the business thinks about customers and orders", the hot spots are:

> `models/staging/*.sql`, `models/customers.sql`, and `models/orders.sql`.

---

### 5. What has changed most frequently in the last 90 days (git velocity map)?

**90-day result (as of 2026-03-10):** no files changed.  
The repo was archived on 2025-02-10, and the latest commit on `main` is 2024-04-18 (README disclaimer updates), so the last-90-day velocity is exactly zero across the codebase.

Because velocity is flat in the target window, the most useful signal is historical concentration of edits:
- **`models/customers.sql` and `models/orders.sql`** saw clustered updates (notably around 2021-09-09), indicating these were the primary business-logic hot spots.
- **`dbt_project.yml` and `seeds/`** changed during maintenance/compatibility cleanup (notably 2022-02-08).
- **`README.md`** was touched most recently (2024-04-18), but those were governance/disclaimer edits rather than transformation logic changes.

Interpretation for Day-One onboarding: this repo has **no current operational churn**, so git velocity cannot identify present-day risk areas. For active brownfield systems, this same analysis would highlight fragile modules, ownership handoffs, and likely incident surfaces.

---

## Difficulty & Confusion Log (What Was Hard Manually?)

1. **Repo naming / redirection friction**  
   - The assignment references `https://github.com/dbt-labs/jaffle-shop`, but GitHub currently surfaces `dbt-labs/jaffle-shop-classic` as the archived, canonical project for this content.  
   - It took a moment to confirm that `jaffle-shop-classic` is still the relevant small dbt demo and that newer repos are not required for this specific Phase 0 task.

2. **Ingestion vs. "real" pipelines**  
   - The README emphasizes that this project uses **seeds instead of sources**, specifically as an anti-pattern to keep things self-contained.  
   - From an FDE perspective, that blurs the line between "ingestion" and "local test data"—there is no upstream ingestion system (Fivetran, Airbyte, custom ELT) visible.  
   - I had to mentally reinterpret `dbt seed` as the practical ingestion step, even though in a real client engagement seeds would not be the true source.

3. **Understanding blast radius without a larger ecosystem**  
   - Because this project is tiny and not wired into dashboards, BI tools, or downstream services, estimating blast radius is necessarily speculative.  
   - I inferred impact based on how `customers` and `orders` would typically be used, not on explicit references to dashboards or external consumers in the repo.

4. **Git velocity in an archived project**  
   - The "last 90 days" question doesn’t map well to an archived example repo.  
   - The GitHub UI gives some hints (per-directory commit histories), but there isn’t an obvious high-velocity core in recent time windows—everything is cold.  
   - I had to fall back to a qualitative statement: essentially zero recent velocity, with historically more changes in README and model files.

5. **Limited cross-cutting complexity**  
   - This project is intentionally simple: no macros, no external sources, no complex DAGs.  
   - From a brownfield FDE perspective, the hard parts you would normally worry about—cross-repo dependencies, mixed-language stacks, CI/CD behavior—simply don’t exist here.  
   - That makes it easy to map manually, but it also means this repo under-represents the real-world navigation pain that the later "Brownfield Cartographer" system needs to solve.

---

## Takeaways for Tooling Priorities

Even in this small dbt project, the following capabilities would accelerate understanding:

- **Model lineage visualization:** quickly see `seeds/raw_* → stg_* → customers/orders` as a DAG, with clear direction of data flow.
- **Surface critical marts first:** highlight `customers` and `orders` as top-level, user-facing tables, distinct from staging and raw.
- **Change history overlays:** even though this repo is static now, a tool that overlays per-file change counts over time would have immediately answered the velocity question on a live project.
- **Contextual docs integration:** inlining key bits of `README.md`, `overview.md`, and `schema.yml` alongside the DAG would reduce context-switching when answering the Day-One questions.
