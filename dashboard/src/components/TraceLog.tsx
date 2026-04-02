"use client";
import { useState } from "react";
import type { TraceEntry } from "@/lib/types";

interface Props { entries: TraceEntry[]; }

const METHOD_COLORS: Record<string, string> = {
  "static-analysis": "text-blue-400",
  "llm-inference": "text-purple-400",
  "hybrid-static-llm": "text-cyan-400",
};

export function TraceLog({ entries }: Props) {
  const [expanded, setExpanded] = useState<number | null>(null);

  if (!entries.length) {
    return (
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-6 text-gray-600 text-sm">
        No trace events yet
      </div>
    );
  }

  const recent = [...entries].reverse().slice(0, 50);

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
      <div className="overflow-x-auto max-h-80 overflow-y-auto">
        <table className="w-full text-xs">
          <thead className="sticky top-0 bg-gray-900 border-b border-gray-800">
            <tr className="text-gray-500 uppercase tracking-wider">
              <th className="text-left px-4 py-2">Time</th>
              <th className="text-left px-4 py-2">Agent</th>
              <th className="text-left px-4 py-2">Action</th>
              <th className="text-left px-4 py-2 hidden md:table-cell">Method</th>
              <th className="text-center px-4 py-2">Conf</th>
            </tr>
          </thead>
          <tbody>
            {recent.map((e, i) => {
              const ts = new Date(e.timestamp_utc).toLocaleTimeString();
              const methodColor = METHOD_COLORS[e.analysis_method] ?? "text-gray-400";
              return (
                <>
                  <tr
                    key={i}
                    className="border-b border-gray-800/50 hover:bg-gray-800/30 cursor-pointer transition-colors"
                    onClick={() => setExpanded(expanded === i ? null : i)}
                  >
                    <td className="px-4 py-2 text-gray-600">{ts}</td>
                    <td className="px-4 py-2 text-green-400">{e.agent}</td>
                    <td className="px-4 py-2 text-gray-300">{e.action}</td>
                    <td className={`px-4 py-2 hidden md:table-cell ${methodColor}`}>
                      {e.analysis_method}
                    </td>
                    <td className="px-4 py-2 text-center">
                      <span className={`${e.confidence > 0.8 ? "text-green-400" : e.confidence > 0.5 ? "text-yellow-400" : "text-red-400"}`}>
                        {(e.confidence * 100).toFixed(0)}%
                      </span>
                    </td>
                  </tr>
                  {expanded === i && (
                    <tr key={`exp-${i}`} className="bg-gray-800/50">
                      <td colSpan={5} className="px-4 py-3">
                        <div className="space-y-1">
                          {e.evidence_sources?.map((ev, j) => (
                            <div key={j} className="text-gray-500 font-mono">
                              {ev.file}:{ev.line_range} [{ev.method}]
                            </div>
                          ))}
                          {e.metadata && Object.keys(e.metadata).length > 0 && (
                            <div className="text-gray-600">
                              {JSON.stringify(e.metadata, null, 2).slice(0, 200)}
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
