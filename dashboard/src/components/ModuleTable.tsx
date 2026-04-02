"use client";
import { useState } from "react";
import type { ModulePurpose } from "@/lib/types";

interface Props { modules: ModulePurpose[]; }

export function ModuleTable({ modules }: Props) {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<"all" | "drift">("all");

  const filtered = modules.filter((m) => {
    const matchSearch =
      m.path.toLowerCase().includes(search.toLowerCase()) ||
      m.purpose_statement.toLowerCase().includes(search.toLowerCase());
    const matchFilter = filter === "all" || (filter === "drift" && m.documentation_drift);
    return matchSearch && matchFilter;
  });

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
      {/* Controls */}
      <div className="flex items-center gap-3 p-3 border-b border-gray-800">
        <input
          type="text"
          placeholder="Search modules…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-200 placeholder-gray-500 outline-none focus:border-cyan-500"
        />
        <button
          onClick={() => setFilter(filter === "all" ? "drift" : "all")}
          className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
            filter === "drift"
              ? "border-yellow-500 text-yellow-400 bg-yellow-500/10"
              : "border-gray-700 text-gray-400 hover:border-gray-500"
          }`}
        >
          ⚠ Doc Drift Only
        </button>
        <span className="text-xs text-gray-600">{filtered.length}/{modules.length}</span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-gray-800 text-gray-500 uppercase tracking-wider">
              <th className="text-left px-4 py-2">Module</th>
              <th className="text-left px-4 py-2 hidden md:table-cell">Domain</th>
              <th className="text-left px-4 py-2">Purpose</th>
              <th className="text-center px-4 py-2">Drift</th>
            </tr>
          </thead>
          <tbody>
            {filtered.slice(0, 50).map((m) => (
              <tr key={m.path} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                <td className="px-4 py-2 font-mono text-blue-400 max-w-[180px] truncate" title={m.path}>
                  {m.path.split(/[\\/]/).pop()}
                </td>
                <td className="px-4 py-2 hidden md:table-cell">
                  <span className="bg-gray-800 px-2 py-0.5 rounded text-purple-300">
                    {m.inferred_domain ?? "—"}
                  </span>
                </td>
                <td className="px-4 py-2 text-gray-400 max-w-xs truncate" title={m.purpose_statement}>
                  {m.purpose_statement}
                </td>
                <td className="px-4 py-2 text-center">
                  {m.documentation_drift ? (
                    <span title={m.documentation_drift_reason ?? ""} className="text-yellow-400 cursor-help">⚠</span>
                  ) : (
                    <span className="text-green-600">✓</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div className="text-center py-8 text-gray-600 text-sm">No modules match your filter</div>
        )}
      </div>
    </div>
  );
}
