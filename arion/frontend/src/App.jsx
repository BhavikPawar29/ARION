// frontend/src/App.jsx
import React, { useEffect, useState } from "react";
import { motion } from 'framer-motion';
import { Cloud, Activity, ShieldCheck, Zap } from 'lucide-react';

import { fetchRisk } from "./api";

const AGENTS = [
  { id: 'market-direction', title: 'Market Direction Agent', desc: 'Observes macro and micro directional signals to estimate trend probabilities and regime shifts.', badge: 'Direction' },
  { id: 'liquidity', title: 'Liquidity Agent', desc: 'Monitors volumes, spreads, and funding dynamics to surface liquidity deterioration early.', badge: 'Liquidity' },
  { id: 'correlation', title: 'Correlation Agent', desc: 'Detects emergent correlations across assets that may amplify downside risk.', badge: 'Correlation' },
  { id: 'tail-risk', title: 'Tail Risk Agent', desc: 'Evaluates extreme event exposure across the portfolio and produces stress scenarios.', badge: 'Tail Risk' },
];

function Hero({ riskSummary, loadingRisk }) {
  return (
    <header className="bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-900 text-white">
      <div className="max-w-7xl mx-auto px-6 py-20 lg:py-28">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          <div>
            <motion.h1 initial={{ y: 12, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.6 }} className="text-4xl md:text-5xl font-extrabold leading-tight">ARION</motion.h1>
            <motion.p initial={{ y: 8, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.12 }} className="mt-4 text-lg text-slate-200 max-w-xl">
              Designed to think in probabilities — an agential AI network that watches, discerns, and foresees risk before it blooms.
            </motion.p>

            <div className="mt-8 flex flex-col sm:flex-row gap-3">
              <a href="#demo" className="inline-flex items-center justify-center rounded-full bg-indigo-500 hover:bg-indigo-600 px-5 py-3 text-base font-semibold shadow-md">See ARION in action</a>
              <a href="#contact" className="inline-flex items-center justify-center rounded-full bg-transparent border border-slate-300/20 text-slate-200 px-5 py-3 text-base font-medium hover:bg-white/5">Contact Sales</a>
            </div>

            <div className="mt-10 grid grid-cols-3 gap-4 max-w-md">
              <Stat icon={<Activity size={18} />} title="Continuous" value="24/7" />
              <Stat icon={<ShieldCheck size={18} />} title="Interpretable" value="Human-first" />
              <Stat icon={<Zap size={18} />} title="Responsive" value="Actionable" />
            </div>

            {/* Risk summary card */}
            <div className="mt-6">
              {loadingRisk ? (
                <div className="text-sm text-slate-200">Loading live risk…</div>
              ) : riskSummary ? (
                <div className="inline-flex items-center gap-6 bg-white/5 px-4 py-3 rounded-lg mt-3">
                  <div>
                    <div className="text-xs text-slate-200">Unified Risk Score</div>
                    <div className="text-2xl font-semibold">{riskSummary.unified_risk_score !== null ? riskSummary.unified_risk_score.toFixed(1) : "—"}/100</div>
                    <div className="text-sm text-slate-300">{riskSummary.risk_level ?? "—"}</div>
                  </div>
                  <div className="text-sm text-slate-300">
                    <div>Risk: {riskSummary.agent_signals?.risk_agent ?? "—"}</div>
                    <div>Forecast: {riskSummary.agent_signals?.forecast_agent ?? "—"}</div>
                  </div>
                </div>
              ) : (
                <div className="text-sm text-slate-200">No risk data available.</div>
              )}
            </div>
          </div>

          <div className="relative">
            <div className="rounded-2xl bg-slate-800/40 p-6">
              <MarketMock />
            </div>
            <div className="absolute -bottom-6 left-6 p-2 bg-white/5 rounded-xl text-xs">Live probabilistic heatmap</div>
          </div>
        </div>
      </div>
    </header>
  );
}

function Stat({ icon, title, value }) {
  return (
    <div className="flex items-center gap-3 bg-slate-900/30 p-3 rounded-lg">
      <div className="p-2 bg-white/5 rounded-md">{icon}</div>
      <div>
        <div className="text-sm text-slate-300">{title}</div>
        <div className="text-base font-semibold">{value}</div>
      </div>
    </div>
  );
}

function MarketMock() {
  return (
    <div className="w-full h-64 flex items-center justify-center">
      <div className="w-full h-full rounded-lg bg-gradient-to-b from-slate-700 to-slate-800 p-4">
        <div className="h-full relative">
          <div className="absolute left-4 top-4 text-xs text-slate-300">Portfolio Risk</div>
          <div className="absolute right-4 bottom-4 text-xs text-slate-300">Live</div>
          <div className="w-full h-full flex items-end">
            {[30,48,36,65,52,78,54,90].map((v,i)=>(
              <div key={i} className="flex-1 mx-1">
                <div style={{height:`${v}%`}} className="w-full rounded-t-md bg-gradient-to-t from-red-500/80 to-yellow-400/80"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function WhyArion(){ /* keep unchanged — your original */ return (
  <section className="py-16 bg-white">
    <div className="max-w-6xl mx-auto px-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
        <div>
          <h2 className="text-2xl font-bold">Why ARION?</h2>
          <p className="mt-4 text-slate-600">Markets move fast and risks compound. ARION provides a network of specialized agents that collaboratively monitor, detect, and propose mitigations — enabling teams to act earlier and with greater clarity.</p>
        </div>
        <div className="bg-slate-50 rounded-xl p-6">
          <h3 className="font-semibold">Quick Flow</h3>
          <ol className="mt-4 list-decimal list-inside space-y-2 text-slate-600">
            <li>Observes live feeds and compute features</li>
            <li>Agents propose probability-weighted alerts</li>
            <li>Network aggregates and ranks vulnerabilities</li>
            <li>Suggested actions with rationale are surfaced to managers</li>
          </ol>
        </div>
      </div>
    </div>
  </section>
); }

function AgentsGrid(){ /* unchanged */ return (
  <section className="py-16 bg-slate-50">
    <div className="max-w-6xl mx-auto px-6">
      <h2 className="text-2xl font-bold mb-6">Agent Network</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {AGENTS.map((a)=>(
          <motion.div key={a.id} whileHover={{y:-6}} className="p-5 rounded-xl bg-white shadow-sm border">
            <div className="flex items-center justify-between">
              <div className="font-semibold">{a.title}</div>
              <div className="text-xs text-slate-500 px-2 py-1 rounded-md bg-slate-100">{a.badge}</div>
            </div>
            <p className="mt-3 text-sm text-slate-600">{a.desc}</p>
            <div className="mt-4 flex items-center gap-2 text-xs text-slate-500">
              <div className="px-2 py-1 rounded bg-indigo-50">Prob: 12%</div>
              <div className="px-2 py-1 rounded bg-yellow-50">Severity: Medium</div>
            </div>
            <div className="mt-4 flex gap-2">
              <button className="text-sm px-3 py-2 rounded bg-indigo-500 text-white">Inspect</button>
              <button className="text-sm px-3 py-2 rounded border">Simulate</button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  </section>
); }

function CTA(){ /* unchanged */ return (
  <section id="demo" className="py-16 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white">
    <div className="max-w-4xl mx-auto px-6 text-center">
      <h3 className="text-2xl font-bold">Want to see ARION monitoring your portfolio?</h3>
      <p className="mt-3 text-slate-100/90">Book a demo and we’ll walk you through live signals, explanations, and suggested mitigations.</p>
      <div className="mt-6 flex items-center justify-center gap-4">
        <a href="#contact" className="px-6 py-3 rounded-full bg-white text-indigo-700 font-semibold">Request demo</a>
        <a href="#docs" className="px-6 py-3 rounded-full border border-white/30">Read docs</a>
      </div>
    </div>
  </section>
); }

function Footer(){ return (
  <footer className="bg-slate-900 text-slate-300 py-8">
    <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
      <div>© {new Date().getFullYear()} ARION — Autonomous Risk Intelligence</div>
      <div className="text-sm">Designed to think in probabilities.</div>
    </div>
  </footer>
); }

export default function App() {
  const [riskSummary, setRiskSummary] = useState(null);
  const [loadingRisk, setLoadingRisk] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        setLoadingRisk(true);
        const data = await fetchRisk();
        setRiskSummary(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingRisk(false);
      }
    }
    load();
  }, []);

  return (
    <div className="min-h-screen font-sans text-slate-800 bg-white">
      <Hero riskSummary={riskSummary} loadingRisk={loadingRisk} />
      <WhyArion />
      <AgentsGrid />
      <CTA />
      <Footer />
    </div>
  )
}
