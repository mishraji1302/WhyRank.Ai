import React from 'react';
import { Terminal, Sparkles, Cpu, Zap } from 'lucide-react';

export default function Header() {
  return (
    <header className="bg-black border-b border-yellow-500/30 sticky top-0 z-50 py-3 shadow-[0_4px_20px_rgba(0,0,0,0.9)]">
      <div className="max-w-[1550px] mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
        {/* Brand Logo */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-yellow-400 text-black flex items-center justify-center font-black shadow-[0_0_15px_rgba(250,204,21,0.4)]">
            <Terminal className="w-5 h-5 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-black text-white tracking-wider font-mono text-glow-yellow">
                WhyRank<span className="text-yellow-400">.ai</span>
              </h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-yellow-400/10 text-yellow-400 border border-yellow-400/30 font-bold flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-yellow-400 animate-ping" />
                PROTOTYPE 1.0 (BETA RELEASE)
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              Explainable Multi-Signal IR & PyTorch Neural Re-Ranker
            </p>
          </div>
        </div>

        {/* Tech Badges */}
        <div className="hidden md:flex items-center gap-3 text-xs font-mono">
          <div className="flex items-center gap-1.5 bg-zinc-900 px-3 py-1.5 rounded-lg border border-yellow-500/30 text-yellow-400 shadow-[0_0_10px_rgba(250,204,21,0.1)]">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Dense MiniLM</span>
          </div>
          <div className="flex items-center gap-1.5 bg-zinc-900 px-3 py-1.5 rounded-lg border border-yellow-500/30 text-yellow-400 shadow-[0_0_10px_rgba(250,204,21,0.1)]">
            <Zap className="w-3.5 h-3.5" />
            <span>BM25 Lexical</span>
          </div>
          <div className="flex items-center gap-1.5 bg-zinc-900 px-3 py-1.5 rounded-lg border border-yellow-500/30 text-yellow-400 shadow-[0_0_10px_rgba(250,204,21,0.1)]">
            <Cpu className="w-3.5 h-3.5" />
            <span>PageRank Graph</span>
          </div>
          <div className="flex items-center gap-1.5 bg-zinc-900 px-3 py-1.5 rounded-lg border border-yellow-500/30 text-yellow-400 shadow-[0_0_10px_rgba(250,204,21,0.1)]">
            <Zap className="w-3.5 h-3.5" />
            <span>Freshness Decay</span>
          </div>
        </div>
      </div>
    </header>
  );
}
