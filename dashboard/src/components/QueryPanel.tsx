"use client";
import { useState } from "react";

const EXAMPLES = [
  "Where is the ingestion logic implemented?",
  "What upstream sources feed the orders dataset?",
  "What is the blast radius of src/agents/hydrologist.py?",
  "Explain what src/agents/surveyor.py does",
];

export function QueryPanel() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  async function submit(q?: string) {
    const query = q ?? question;
    if (!query.trim()) return;
    setQuestion(query);
    setLoading(true);
    setAnswer(null);
    setError(false);

    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: query }),
      });
      const data = await res.json();
      setAnswer(data.answer);
      setError(!!data.error);
    } catch (e) {
      setAnswer("Network error — is the dev server running?");
      setError(true);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 space-y-4">
      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="Ask the Navigator…"
          className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-500 outline-none focus:border-cyan-500"
        />
        <button
          onClick={() => submit()}
          disabled={loading}
          className="bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-sm px-4 py-2 rounded-lg transition-colors"
        >
          {loading ? "…" : "Ask"}
        </button>
      </div>

      {/* Example chips */}
      <div className="flex flex-wrap gap-2">
        {EXAMPLES.map((e) => (
          <button
            key={e}
            onClick={() => submit(e)}
            className="text-xs bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-400 hover:text-cyan-400 px-2 py-1 rounded-lg transition-colors"
          >
            {e}
          </button>
        ))}
      </div>

      {/* Answer */}
      {answer && (
        <div className={`rounded-lg p-4 text-sm whitespace-pre-wrap font-mono ${
          error ? "bg-red-950 border border-red-800 text-red-300" : "bg-gray-800 border border-gray-700 text-gray-200"
        }`}>
          {answer}
        </div>
      )}
    </div>
  );
}
