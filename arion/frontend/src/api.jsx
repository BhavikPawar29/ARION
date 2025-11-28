const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export async function fetchRisk(symbols = "AAPL,MSFT,GOOGL,TSLA,NVDA", period = "3mo") {
  const url = `${API_BASE}/api/risk?symbols=${encodeURIComponent(symbols)}&period=${encodeURIComponent(period)}`;
  const res = await fetch(url);
  if (!res.ok) {
    const msg = `API error ${res.status}`;
    throw new Error(msg);
  }
  return res.json();
}
