"use client";
import { useCartographyData } from "@/lib/hooks";
import { OverviewCards } from "@/components/OverviewCards";
import { FDEAnswers } from "@/components/FDEAnswers";
import { ModuleGraph } from "@/components/ModuleGraph";
import { DomainChart } from "@/components/DomainChart";
import { ModuleTable } from "@/components/ModuleTable";
import { TraceLog } from "@/components/TraceLog";
import { QueryPanel } from "@/components/QueryPanel";
import { NavBar } from "@/components/NavBar";

export default function Home() {
  const { data, loading, error } = useCartographyData();

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center text-gray-400">
        <div className="text-center">
          <div className="text-4xl mb-4">⚙</div>
          <p>Loading cartography artifacts…</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex h-screen items-center justify-center text-red-400">
        <div className="text-center max-w-md">
          <div className="text-4xl mb-4">⚠</div>
          <p className="text-lg font-semibold mb-2">No artifacts found</p>
          <p className="text-sm text-gray-500">
            Run <code className="bg-gray-800 px-2 py-0.5 rounded">python main.py analyze .</code> in
            the project root first, then refresh.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950">
      <NavBar />
      <main className="max-w-7xl mx-auto px-4 py-6 space-y-8">
        {/* Overview stats */}
        <OverviewCards data={data} />

        {/* FDE Day-One answers */}
        <section id="fde">
          <h2 className="text-lg font-semibold text-cyan-400 mb-3 flex items-center gap-2">
            <span>🧭</span> Five FDE Day-One Answers
          </h2>
          <FDEAnswers answers={data.semanticReport?.five_fde_day_one_answers ?? null} />
        </section>

        {/* Module graph + Domain chart */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6" id="graph">
          <section>
            <h2 className="text-lg font-semibold text-cyan-400 mb-3 flex items-center gap-2">
              <span>🗺</span> Module Graph
            </h2>
            <ModuleGraph graph={data.moduleGraph} />
          </section>
          <section>
            <h2 className="text-lg font-semibold text-cyan-400 mb-3 flex items-center gap-2">
              <span>🏷</span> Domain Boundaries
            </h2>
            <DomainChart domains={data.semanticReport?.business_domain_boundaries ?? []} />
          </section>
        </div>

        {/* Lineage sources / sinks */}
        <section id="lineage">
          <h2 className="text-lg font-semibold text-cyan-400 mb-3 flex items-center gap-2">
            <span>🔗</span> Data Lineage
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Sources</p>
              {data.lineageMeta.sources.length === 0 ? (
                <p className="text-gray-600 text-sm">No sources detected</p>
              ) : (
                <ul className="space-y-1">
                  {data.lineageMeta.sources.map((s) => (
                    <li key={s} className="text-xs text-green-400 font-mono bg-gray-800 rounded px-2 py-1">{s}</li>
                  ))}
                </ul>
              )}
            </div>
            <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Sinks</p>
              {data.lineageMeta.sinks.length === 0 ? (
                <p className="text-gray-600 text-sm">No sinks detected</p>
              ) : (
                <ul className="space-y-1">
                  {data.lineageMeta.sinks.map((s) => (
                    <li key={s} className="text-xs text-orange-400 font-mono bg-gray-800 rounded px-2 py-1">{s}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </section>

        {/* Module purpose table */}
        <section id="modules">
          <h2 className="text-lg font-semibold text-cyan-400 mb-3 flex items-center gap-2">
            <span>📦</span> Module Purpose Index
          </h2>
          <ModuleTable modules={data.semanticReport?.module_purpose_statements ?? []} />
        </section>

        {/* Query panel */}
        <section id="query">
          <h2 className="text-lg font-semibold text-cyan-400 mb-3 flex items-center gap-2">
            <span>💬</span> Navigator Query
          </h2>
          <QueryPanel />
        </section>

        {/* Trace log */}
        <section id="trace">
          <h2 className="text-lg font-semibold text-cyan-400 mb-3 flex items-center gap-2">
            <span>📋</span> Cartography Trace Log
          </h2>
          <TraceLog entries={data.traceLog} />
        </section>
      </main>
    </div>
  );
}
