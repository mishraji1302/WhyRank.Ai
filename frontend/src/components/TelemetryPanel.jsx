import React, { useState } from 'react';
import { Activity, Database, GitFork, Cpu, Zap, Info } from 'lucide-react';

const CORA_CATEGORIES = [
  { name: "Neural Networks", count: 818, query: "neural networks backpropagation" },
  { name: "Probabilistic Methods", count: 426, query: "probabilistic methods bayesian inference" },
  { name: "Genetic Algorithms", count: 418, query: "genetic algorithms crossover" },
  { name: "Theory", count: 351, query: "computational learning theory PAC bounds" },
  { name: "Case Based", count: 298, query: "case based reasoning similarity" },
  { name: "Reinforcement Learning", count: 217, query: "reinforcement learning policy gradient" },
  { name: "Rule Learning", count: 180, query: "rule learning inductive logic" },
];

const CORA_DEFINITION = "CORA Dataset: Benchmark Machine Learning corpus containing 2,708 scientific papers across 7 categories linked by 5,429 citation graph edges.";

export default function TelemetryPanel({ onSelectCategory }) {
  const [showCoraInfo, setShowCoraInfo] = useState(false);

  return (
    <aside className="space-y-5 font-mono">
      {/* Telemetry Card */}
      <div className="yellow-card p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-yellow-400" />
            <span className="text-xs font-bold text-white uppercase tracking-wider">Telemetry</span>
          </div>
          <span className="flex h-2.5 w-2.5 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-yellow-400"></span>
          </span>
        </div>

        <div className="space-y-2.5 text-xs">
          <div className="flex justify-between items-center black-inset p-2.5">
            <span className="text-zinc-400 flex items-center gap-1.5 font-bold">
              <Database className="w-3.5 h-3.5 text-yellow-400" /> Corpus Size
            </span>
            <span className="font-bold text-yellow-300 font-mono">2,708 Papers</span>
          </div>

          <div className="flex justify-between items-center black-inset p-2.5">
            <span className="text-zinc-400 flex items-center gap-1.5 font-bold">
              <GitFork className="w-3.5 h-3.5 text-yellow-400" /> Citation Graph
            </span>
            <span className="font-bold text-yellow-300 font-mono">5,429 Edges</span>
          </div>

          <div className="flex justify-between items-center black-inset p-2.5">
            <span className="text-zinc-400 flex items-center gap-1.5 font-bold">
              <Cpu className="w-3.5 h-3.5 text-yellow-400" /> Embeddings
            </span>
            <span className="font-bold text-yellow-300 text-[10px]">MiniLM-L6-v2</span>
          </div>

          <div className="flex justify-between items-center black-inset p-2.5">
            <span className="text-zinc-400 flex items-center gap-1.5 font-bold">
              <Zap className="w-3.5 h-3.5 text-yellow-400" /> Target Latency
            </span>
            <span className="font-bold text-yellow-300">&lt; 500 ms SLA</span>
          </div>
        </div>
      </div>

      {/* CORA Categories */}
      <div className="yellow-card p-5 space-y-3">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
          <div className="flex items-center gap-1.5">
            <span className="text-xs font-bold text-yellow-400 uppercase tracking-wider">CORA Categories</span>
            <button
              type="button"
              onClick={() => setShowCoraInfo(!showCoraInfo)}
              className="text-yellow-400/70 hover:text-yellow-400 transition-colors p-0.5 rounded-full hover:bg-yellow-400/10"
              title="View CORA dataset definition"
            >
              <Info className="w-3.5 h-3.5" />
            </button>
          </div>
          <span className="text-[10px] text-yellow-300 font-bold">7 Domains</span>
        </div>

        {showCoraInfo && (
          <div className="text-[11px] text-yellow-200 bg-yellow-400/10 p-2.5 rounded-lg border border-yellow-400/30 leading-relaxed font-sans">
            {CORA_DEFINITION}
          </div>
        )}

        <div className="space-y-1.5">
          {CORA_CATEGORIES.map((cat) => (
            <button
              key={cat.name}
              type="button"
              onClick={() => onSelectCategory(cat.query)}
              className="w-full p-2.5 rounded-xl bg-black/60 border border-zinc-800 hover:border-yellow-400/50 hover:bg-zinc-900 transition-all flex items-center justify-between text-left text-xs group"
            >
              <span className="text-slate-300 group-hover:text-yellow-300 transition-colors">{cat.name}</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-900 text-yellow-400 border border-yellow-400/20 group-hover:bg-yellow-400 group-hover:text-black font-bold transition-all">
                {cat.count}
              </span>
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}
