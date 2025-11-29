// frontend/src/App.jsx
import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import SymbolPanel from "./components/SymbolPanel.jsx";
import { fetchRisk } from "./api";

function Hero({ riskSummary, loadingRisk }) {
  return (
    <header className="bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-900 text-white">
      <div className="max-w-7xl mx-auto px-6 py-20 lg:py-28">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          <div>
            <motion.h1 initial={{ y: 12, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.6 }} className="text-4xl md:text-5xl font-extrabold leading-tight">
              ARION
            </motion.h1>
            <motion.p initial={{ y: 8, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.12 }} className="mt-4 text-lg text-slate-200 max-w-xl">
              Designed to think in probabilities — an agential AI network that watches, discerns, and foresees risk before it blooms.
            </motion.p>

            {/* simplified: no stat cards */}
            <div className="mt-6">
              {loadingRisk ? (
                <div className="text-sm text-slate-200">Loading live risk…</div>
              ) : riskSummary ? (
                <div className="inline-flex items-center gap-6 bg-white/5 px-4 py-3 rounded-lg mt-3">
                  <div>
                    <div className="text-xs text-slate-200">Unified Risk Score</div>
                    <div className="text-2xl font-semibold">
                      {riskSummary.unified_risk_score !== null && riskSummary.unified_risk_score !== undefined ? riskSummary.unified_risk_score.toFixed(1) : "—"}/100
                    </div>
                    <div className="text-sm text-slate-300">{riskSummary.risk_level ?? "—"}</div>
                  </div>
                </div>
              ) : (
                <div className="text-sm text-slate-200">No risk data available.</div>
              )}
            </div>
          </div>

          <div className="relative">
            <div className="rounded-2xl bg-slate-800/40 p-6">
              <div style={{height: 260}} />
            </div>
            <div className="absolute -bottom-6 left-6 p-2 bg-white/5 rounded-xl text-xs">Live probabilistic heatmap</div>
          </div>
        </div>
      </div>
    </header>
  );
}

function WhyArion() {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-6xl mx-auto px-6">
        <h2 className="text-2xl font-bold">Why ARION?</h2>
        <p className="mt-4 text-slate-600">
          Markets move fast and risks compound. ARION provides a network of specialized agents that collaboratively monitor, detect, and propose mitigations — enabling teams to act earlier and with greater clarity.
        </p>
      </div>
    </section>
  );
}

function CTA() {
  return (
    <section id="demo" className="py-16 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white">
      <div className="max-w-4xl mx-auto px-6 text-center">
        <h3 className="text-2xl font-bold">Want to see ARION monitoring your portfolio?</h3>
        <div className="mt-6 flex items-center justify-center gap-4">
          <a href="#contact" className="px-6 py-3 rounded-full bg-white text-indigo-700 font-semibold">Request demo</a>
          <a href="#docs" className="px-6 py-3 rounded-full border border-white/30">Read docs</a>
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-300 py-8">
      <div className="max-w-6xl mx-auto px-6 flex items-center justify-between">
        <div>© {new Date().getFullYear()} ARION — Autonomous Risk Intelligence</div>
        <div className="text-sm">Designed to think in probabilities.</div>
      </div>
    </footer>
  );
}

export default function App() {
  const [riskSummary, setRiskSummary] = useState(null);
  const [loadingRisk, setLoadingRisk] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        setLoadingRisk(true);
        // keep initial load short; avoid long waits
        const data = await fetchRisk(["AAPL","MSFT","GOOGL"]);
        setRiskSummary(data);
      } catch (err) {
        console.error("initial fetch failed", err);
      } finally {
        setLoadingRisk(false);
      }
    }
    load();
  }, []);

  return (
    <div className="min-h-screen font-sans text-slate-800 bg-white">
      <Hero riskSummary={riskSummary} loadingRisk={loadingRisk} />

      {/* SYMBOL INPUT + RESULTS */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        <SymbolPanel onResult={(res) => setRiskSummary(res)} />
      </div>

      <WhyArion />
      <CTA />
      <Footer />
    </div>
  );
}
