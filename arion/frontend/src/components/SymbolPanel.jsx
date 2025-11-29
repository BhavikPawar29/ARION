// frontend/src/components/SymbolPanel.jsx
import React, { useState } from "react";
import { fetchRisk, triggerCycle } from "../api";

function normalizeSymbols(raw) {
  if (!raw) return [];
  const toks = raw.split(/[\s,;]+/).map(s=>s.trim().toUpperCase()).filter(Boolean);
  return Array.from(new Set(toks)).slice(0, 12);
}

export default function SymbolPanel({ onResult }) {
  const [text, setText] = useState("AAPL");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastSymbols, setLastSymbols] = useState([]);

  async function handleAnalyze() {
    setError("");
    const syms = normalizeSymbols(text);
    if (syms.length === 0) {
      setError("Enter tickers (comma/space separated).");
      return;
    }
    setLoading(true);
    try {
      const res = await fetchRisk(syms);
      setLastSymbols(syms);
      onResult?.(res);
    } catch (e) {
      console.error(e);
      setError("API call failed. Check backend logs.");
    } finally {
      setLoading(false);
    }
  }

  async function handleTrigger() {
    setError("");
    const syms = normalizeSymbols(text);
    const event = { symbol: syms[0] ?? "AAPL", shock: "-5%" };
    setLoading(true);
    try {
      const res = await triggerCycle(event);
      onResult?.(res);
    } catch (e) {
      setError("Trigger failed");
    } finally {
      setLoading(false);
    }
  }

  function handleClear() {
    setText("");
    setLastSymbols([]);
    setError("");
  }

  return (
    <div className="p-4 bg-white border rounded-lg shadow-sm">
      <h3 className="text-lg font-semibold mb-2">Symbols</h3>
      <textarea value={text} onChange={(e)=>setText(e.target.value)} rows={3}
        className="w-full p-2 border rounded mb-3" placeholder="AAPL, MSFT, TSLA" />
      <div className="flex gap-2 mb-3">
        <button onClick={handleAnalyze} className="bg-indigo-600 text-white px-4 py-2 rounded" disabled={loading}>{loading ? "Analyzing…" : "Analyze"}</button>
        <button onClick={handleTrigger} className="bg-yellow-500 text-white px-4 py-2 rounded" disabled={loading}>{loading ? "Triggering…" : "Trigger (demo)"}</button>
        <button onClick={handleClear} className="px-4 py-2 border rounded">Clear</button>
      </div>

      <div className="text-sm text-slate-600 mb-2">Symbols used: {lastSymbols.join(", ") || "—"}</div>
      <div>
        <strong>Unified risk score:</strong> <span className="ml-2">— / unknown</span>
      </div>
    </div>
  );
}
