// frontend/src/api.js
const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export async function fetchRisk(symbols, period="3mo") {
  if (!symbols || symbols.length === 0) {
    throw new Error("No symbols provided");
  }
  const qs = new URLSearchParams({ symbols: symbols.join(","), period });
  const res = await fetch(`${API_BASE}/api/risk?${qs.toString()}`);
  if (!res.ok) {
    const t = await res.text();
    throw new Error(`API ${res.status}: ${t}`);
  }
  return res.json();
}

export async function triggerCycle(market_event = {}) {
  const res = await fetch(`${API_BASE}/api/trigger`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ market_event }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}
