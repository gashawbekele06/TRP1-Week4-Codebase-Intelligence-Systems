"use client";
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import type { DomainBoundary } from "@/lib/types";

const COLORS = ["#06b6d4","#a855f7","#f97316","#22c55e","#eab308","#3b82f6","#ec4899","#14b8a6"];

interface Props { domains: DomainBoundary[]; }

export function DomainChart({ domains }: Props) {
  if (!domains.length) {
    return (
      <div className="bg-gray-900 rounded-xl border border-gray-800 h-72 flex items-center justify-center text-gray-600 text-sm">
        No domain data available
      </div>
    );
  }

  const data = domains.map((d) => ({
    name: d.domain,
    value: d.module_count,
  }));

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-4" style={{ height: 380 }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="45%"
            outerRadius={110}
            dataKey="value"
            label={({ name, value }) => `${name} (${value})`}
            labelLine={false}
            fontSize={10}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ background: "#1f2937", border: "1px solid #374151", borderRadius: 8 }}
            labelStyle={{ color: "#e5e7eb" }}
          />
          <Legend
            formatter={(value) => <span style={{ color: "#9ca3af", fontSize: 11 }}>{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
