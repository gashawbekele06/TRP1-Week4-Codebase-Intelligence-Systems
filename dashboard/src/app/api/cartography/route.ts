import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const CART_DIR = path.join(process.cwd(), "..", ".cartography");

function readJson(file: string) {
  const p = path.join(CART_DIR, file);
  if (!fs.existsSync(p)) return null;
  try {
    return JSON.parse(fs.readFileSync(p, "utf-8"));
  } catch {
    return null;
  }
}

function readText(file: string): string | null {
  const p = path.join(CART_DIR, file);
  if (!fs.existsSync(p)) return null;
  try {
    return fs.readFileSync(p, "utf-8");
  } catch {
    return null;
  }
}

function readJsonL(file: string) {
  const p = path.join(CART_DIR, file);
  if (!fs.existsSync(p)) return [];
  try {
    return fs
      .readFileSync(p, "utf-8")
      .split("\n")
      .filter(Boolean)
      .map((l) => JSON.parse(l));
  } catch {
    return [];
  }
}

export async function GET() {
  const moduleGraph = readJson("module_graph.json");
  const lineageGraph = readJson("lineage_graph.json");
  const semanticReport = readJson("semantic_report.json");
  const codebaseMd = readText("CODEBASE.md");
  const onboardingBrief = readText("onboarding_brief.md");
  const traceLog = readJsonL("cartography_trace.jsonl");

  // Normalise edge key (networkx changed links→edges in v3.4)
  function normaliseGraph(g: Record<string, unknown> | null) {
    if (!g) return null;
    const raw = (g.graph ?? g) as Record<string, unknown>;
    if (!raw.edges && raw.links) raw.edges = raw.links;
    return raw;
  }

  return NextResponse.json({
    moduleGraph: normaliseGraph(moduleGraph),
    lineageGraph: normaliseGraph(
      lineageGraph?.graph ? lineageGraph : { graph: lineageGraph }
    ),
    lineageMeta: {
      sources: lineageGraph?.sources ?? [],
      sinks: lineageGraph?.sinks ?? [],
    },
    semanticReport,
    codebaseMd,
    onboardingBrief,
    traceLog,
  });
}
