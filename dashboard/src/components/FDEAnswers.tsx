"use client";
import type { FDEAnswers as FDEAnswersType } from "@/lib/types";

interface Props { answers: FDEAnswersType | null; }

const QUESTIONS = [
  { key: "q1_primary_ingestion_path", label: "Primary Ingestion Path", icon: "📥" },
  { key: "q2_critical_outputs",       label: "Critical Outputs",        icon: "📤" },
  { key: "q3_blast_radius",           label: "Blast Radius",            icon: "💥" },
  { key: "q4_logic_concentration",    label: "Logic Concentration",     icon: "🧠" },
  { key: "q5_git_velocity_map",       label: "Git Velocity Map",        icon: "🔥" },
] as const;

export function FDEAnswers({ answers }: Props) {
  if (!answers) {
    return (
      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 text-gray-500 text-sm">
        No FDE answers yet — run <code className="bg-gray-800 px-1 rounded">python main.py analyze .</code>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
      {QUESTIONS.map(({ key, label, icon }) => {
        const text = answers[key] ?? "Unavailable";
        // Split evidence from answer
        const evidenceIdx = text.indexOf("Evidence:");
        const answer = evidenceIdx > -1 ? text.slice(0, evidenceIdx).trim() : text;
        const evidence = evidenceIdx > -1 ? text.slice(evidenceIdx + 9).trim() : null;

        return (
          <div key={key} className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <span>{icon}</span>
              <span className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">{label}</span>
            </div>
            <p className="text-sm text-gray-200 leading-relaxed">{answer}</p>
            {evidence && (
              <p className="text-xs text-gray-600 font-mono truncate" title={evidence}>
                {evidence}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}
