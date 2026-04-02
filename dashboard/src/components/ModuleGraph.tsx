"use client";
import { useMemo } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  type Node,
  type Edge,
} from "reactflow";
import "reactflow/dist/style.css";
import type { RawGraph } from "@/lib/types";

interface Props { graph: RawGraph | null; }

const DOMAIN_COLORS: Record<string, string> = {
  ingestion: "#06b6d4",
  transformation: "#a855f7",
  serving: "#f97316",
  orchestration: "#22c55e",
  monitoring: "#eab308",
  analysis: "#3b82f6",
  unknown: "#6b7280",
};

function domainColor(domain?: string) {
  if (!domain) return DOMAIN_COLORS.unknown;
  for (const [k, v] of Object.entries(DOMAIN_COLORS)) {
    if (domain.toLowerCase().includes(k)) return v;
  }
  return DOMAIN_COLORS.unknown;
}

export function ModuleGraph({ graph }: Props) {
  const { nodes, edges } = useMemo(() => {
    if (!graph?.nodes?.length) return { nodes: [], edges: [] };

    const rawEdges = graph.edges ?? graph.links ?? [];
    const count = graph.nodes.length;
    const cols = Math.ceil(Math.sqrt(count));

    const nodes: Node[] = graph.nodes.map((n, i) => {
      const label = n.path
        ? n.path.split(/[\\/]/).pop() ?? n.id
        : n.name ?? n.id;
      const color = domainColor(n.domain_cluster);
      return {
        id: n.id,
        data: { label },
        position: {
          x: (i % cols) * 180 + 20,
          y: Math.floor(i / cols) * 80 + 20,
        },
        style: {
          background: "#1f2937",
          border: `1.5px solid ${color}`,
          color: color,
          fontSize: 10,
          padding: "4px 8px",
          borderRadius: 6,
          maxWidth: 160,
          whiteSpace: "nowrap",
          overflow: "hidden",
          textOverflow: "ellipsis",
        },
      };
    });

    const edges: Edge[] = rawEdges.map((e, i) => ({
      id: `e-${i}`,
      source: String(e.source),
      target: String(e.target),
      style: { stroke: "#374151", strokeWidth: 1 },
      animated: false,
    }));

    return { nodes, edges };
  }, [graph]);

  if (!graph?.nodes?.length) {
    return (
      <div className="bg-gray-900 rounded-xl border border-gray-800 h-72 flex items-center justify-center text-gray-600 text-sm">
        No module graph data — run analysis first
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden" style={{ height: 380 }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#374151" gap={20} />
        <Controls showInteractive={false} />
        <MiniMap nodeColor={() => "#374151"} maskColor="rgba(0,0,0,0.5)" />
      </ReactFlow>
    </div>
  );
}
