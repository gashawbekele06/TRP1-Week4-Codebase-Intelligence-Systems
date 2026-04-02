"use client";
import type { CartographyData } from "@/lib/types";

interface Props { data: CartographyData; }

export function OverviewCards({ data }: Props) {
  const moduleCount = data.moduleGraph?.nodes?.length ?? 0;
  const edgeCount = (data.moduleGraph?.edges ?? data.moduleGraph?.links ?? []).length;
  const lineageNodes = (data.lineageGraph?.nodes ?? []).length;
  const domainCount = data.semanticReport?.business_domain_boundaries?.length ?? 0;
  const driftCount = data.semanticReport?.module_purpose_statements?.filter(
    (m) => m.documentation_drift
  ).length ?? 0;
  const traceCount = data.traceLog?.length ?? 0;

  const cards = [
    { label: "Modules", value: moduleCount, icon: "📦", color: "text-blue-400" },
    { label: "Import Edges", value: edgeCount, icon: "🔗", color: "text-indigo-400" },
    { label: "Lineage Nodes", value: lineageNodes, icon: "🌊", color: "text-cyan-400" },
    { label: "Domains", value: domainCount, icon: "🏷", color: "text-purple-400" },
    { label: "Doc Drift Flags", value: driftCount, icon: "⚠", color: "text-yellow-400" },
    { label: "Trace Events", value: traceCount, icon: "📋", color: "text-green-400" },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      {cards.map((c) => (
        <div key={c.label} className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <div className="text-2xl mb-1">{c.icon}</div>
          <div className={`text-2xl font-bold ${c.color}`}>{c.value}</div>
          <div className="text-xs text-gray-500 mt-1">{c.label}</div>
        </div>
      ))}
    </div>
  );
}
