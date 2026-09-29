import React, { useState } from 'react';
import { Sliders, Sparkles, Layers, ShieldCheck, Clock, Brain, Settings, Check, Info } from 'lucide-react';

const PRESETS = [
  { name: "Balanced", weights: { semantic: 0.40, keyword: 0.25, authority: 0.20, freshness: 0.15 } },
  { name: "Relevance", weights: { semantic: 0.60, keyword: 0.40, authority: 0.00, freshness: 0.00 } },
  { name: "Authority", weights: { semantic: 0.25, keyword: 0.20, authority: 0.55, freshness: 0.00 } },
  { name: "Freshness", weights: { semantic: 0.25, keyword: 0.15, authority: 0.10, freshness: 0.50 } },
];

const PARAMETER_DEFINITIONS = {
  semantic: "Vector Semantic: Measures deep contextual relevance using 384-dimensional dense sentence embeddings (all-MiniLM-L6-v2) to match concepts and synonyms.",
  keyword: "BM25 Lexical: Measures exact keyword matching and document length normalization using Okapi BM25 with Lucene non-negative IDF.",
  authority: "PageRank Graph: Measures document domain authority based on 5,429 citation links using power iteration with sink-node mass redistribution.",
  freshness: "Freshness Decay: Measures publication recency using an exponential decay function with a 5-year half-life."
};

export default function SidebarControls({
  weights,
  setWeights,
  activePreset,
  setActivePreset,
  scoringMode,
  setScoringMode,
  onApply
}) {
  const [activeTooltip, setActiveTooltip] = useState(null);

  const handleSliderChange = (changedKey, newValuePercent) => {
    setActivePreset(null);
    const newValue = newValuePercent / 100;
    const clampedNewValue = Math.min(1, Math.max(0, newValue));

    const otherKeys = Object.keys(weights).filter(k => k !== changedKey);
    const currentOthersSum = otherKeys.reduce((acc, k) => acc + weights[k], 0);

    const remainingMass = 1 - clampedNewValue;
    const newWeights = { ...weights, [changedKey]: clampedNewValue };

    if (currentOthersSum > 0) {
      otherKeys.forEach(k => {
        newWeights[k] = (weights[k] / currentOthersSum) * remainingMass;
      });
    } else {
      const equalShare = remainingMass / otherKeys.length;
      otherKeys.forEach(k => {
        newWeights[k] = equalShare;
      });
    }

    setWeights(newWeights);
    onApply(newWeights, scoringMode);
  };

  const handleSelectPreset = (preset) => {
    setActivePreset(preset.name);
    setWeights(preset.weights);
    onApply(preset.weights, scoringMode);
  };

  const handleToggleMode = (newMode) => {
    setScoringMode(newMode);
    onApply(weights, newMode);
  };

  const toggleTooltip = (paramKey) => {
    setActiveTooltip(activeTooltip === paramKey ? null : paramKey);
  };

  return (
    <aside className="space-y-5 font-mono">
      {/* Engine Mode Card */}
      <div className="yellow-card p-4 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-yellow-400 uppercase tracking-wider">Engine Mode</span>
          <span className="w-2.5 h-2.5 rounded-full bg-yellow-400 animate-pulse shadow-[0_0_8px_#facc15]" />
        </div>

        <div className="grid grid-cols-2 gap-1.5 black-inset p-1 rounded-xl">
          <button
            type="button"
            onClick={() => handleToggleMode('manual')}
            className={`py-2 rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${
              scoringMode === 'manual'
                ? 'bg-yellow-400 text-black shadow-[0_0_12px_rgba(250,204,21,0.4)] font-extrabold'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Settings className="w-3.5 h-3.5" />
            <span>Formula</span>
          </button>

          <button
            type="button"
            onClick={() => handleToggleMode('neural')}
            className={`py-2 rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${
              scoringMode === 'neural'
                ? 'bg-yellow-400 text-black shadow-[0_0_12px_rgba(250,204,21,0.4)] font-extrabold'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Brain className="w-3.5 h-3.5" />
            <span>Neural ML</span>
          </button>
        </div>
      </div>

      {/* Ranking Presets */}
      {scoringMode === 'manual' && (
        <div className="yellow-card p-4 space-y-3">
          <span className="text-xs font-bold text-yellow-400 uppercase tracking-wider">Ranking Presets</span>
          <div className="grid grid-cols-2 gap-2">
            {PRESETS.map((p) => {
              const isActive = activePreset === p.name;
              return (
                <button
                  key={p.name}
                  type="button"
                  onClick={() => handleSelectPreset(p)}
                  className={`px-3 py-2 rounded-xl text-xs font-bold transition-all text-left flex items-center justify-between border ${
                    isActive
                      ? 'bg-yellow-400/20 border-yellow-400 text-yellow-300 shadow-[0_0_10px_rgba(250,204,21,0.2)]'
                      : 'bg-black/60 border-zinc-800 text-slate-400 hover:border-yellow-400/40 hover:text-white'
                  }`}
                >
                  <span>{p.name}</span>
                  {isActive && <Check className="w-3.5 h-3.5 text-yellow-400" />}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Horizontal Sliders Stacked Vertically with Info Buttons */}
      {scoringMode === 'manual' ? (
        <div className="yellow-card p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
            <div className="flex items-center gap-2">
              <Sliders className="w-4 h-4 text-yellow-400" />
              <span className="text-xs font-bold text-white uppercase tracking-wider">Signal Weights</span>
            </div>
            <span className="text-xs font-mono font-bold text-yellow-400 bg-yellow-400/10 px-2 py-0.5 rounded border border-yellow-400/30">
              100%
            </span>
          </div>

          <div className="space-y-4 pt-1">
            {/* Vector Semantic */}
            <div className="space-y-1.5 black-inset p-3 rounded-xl relative">
              <div className="flex justify-between items-center text-xs font-bold">
                <div className="flex items-center gap-1.5 text-yellow-400">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Vector Semantic</span>
                  <button
                    type="button"
                    onClick={() => toggleTooltip('semantic')}
                    className="text-yellow-400/70 hover:text-yellow-400 transition-colors p-0.5 rounded-full hover:bg-yellow-400/10"
                    title="View definition"
                  >
                    <Info className="w-3.5 h-3.5" />
                  </button>
                </div>
                <span className="font-mono text-yellow-300">{Math.round(weights.semantic * 100)}%</span>
              </div>
              {activeTooltip === 'semantic' && (
                <div className="text-[11px] text-yellow-200 bg-yellow-400/10 p-2.5 rounded-lg border border-yellow-400/30 leading-relaxed font-sans mt-1">
                  {PARAMETER_DEFINITIONS.semantic}
                </div>
              )}
              <input
                type="range"
                min="0"
                max="100"
                value={Math.round(weights.semantic * 100)}
                onChange={(e) => handleSliderChange('semantic', Number(e.target.value))}
                className="w-full accent-yellow-400 h-2 bg-zinc-800 rounded-lg cursor-pointer"
              />
            </div>

            {/* BM25 Lexical */}
            <div className="space-y-1.5 black-inset p-3 rounded-xl relative">
              <div className="flex justify-between items-center text-xs font-bold">
                <div className="flex items-center gap-1.5 text-yellow-400">
                  <Layers className="w-3.5 h-3.5" />
                  <span>BM25 Lexical</span>
                  <button
                    type="button"
                    onClick={() => toggleTooltip('keyword')}
                    className="text-yellow-400/70 hover:text-yellow-400 transition-colors p-0.5 rounded-full hover:bg-yellow-400/10"
                    title="View definition"
                  >
                    <Info className="w-3.5 h-3.5" />
                  </button>
                </div>
                <span className="font-mono text-yellow-300">{Math.round(weights.keyword * 100)}%</span>
              </div>
              {activeTooltip === 'keyword' && (
                <div className="text-[11px] text-yellow-200 bg-yellow-400/10 p-2.5 rounded-lg border border-yellow-400/30 leading-relaxed font-sans mt-1">
                  {PARAMETER_DEFINITIONS.keyword}
                </div>
              )}
              <input
                type="range"
                min="0"
                max="100"
                value={Math.round(weights.keyword * 100)}
                onChange={(e) => handleSliderChange('keyword', Number(e.target.value))}
                className="w-full accent-yellow-400 h-2 bg-zinc-800 rounded-lg cursor-pointer"
              />
            </div>

            {/* PageRank Graph */}
            <div className="space-y-1.5 black-inset p-3 rounded-xl relative">
              <div className="flex justify-between items-center text-xs font-bold">
                <div className="flex items-center gap-1.5 text-yellow-400">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>PageRank Graph</span>
                  <button
                    type="button"
                    onClick={() => toggleTooltip('authority')}
                    className="text-yellow-400/70 hover:text-yellow-400 transition-colors p-0.5 rounded-full hover:bg-yellow-400/10"
                    title="View definition"
                  >
                    <Info className="w-3.5 h-3.5" />
                  </button>
                </div>
                <span className="font-mono text-yellow-300">{Math.round(weights.authority * 100)}%</span>
              </div>
              {activeTooltip === 'authority' && (
                <div className="text-[11px] text-yellow-200 bg-yellow-400/10 p-2.5 rounded-lg border border-yellow-400/30 leading-relaxed font-sans mt-1">
                  {PARAMETER_DEFINITIONS.authority}
                </div>
              )}
              <input
                type="range"
                min="0"
                max="100"
                value={Math.round(weights.authority * 100)}
                onChange={(e) => handleSliderChange('authority', Number(e.target.value))}
                className="w-full accent-yellow-400 h-2 bg-zinc-800 rounded-lg cursor-pointer"
              />
            </div>

            {/* Freshness Decay */}
            <div className="space-y-1.5 black-inset p-3 rounded-xl relative">
              <div className="flex justify-between items-center text-xs font-bold">
                <div className="flex items-center gap-1.5 text-yellow-400">
                  <Clock className="w-3.5 h-3.5" />
                  <span>Freshness Decay</span>
                  <button
                    type="button"
                    onClick={() => toggleTooltip('freshness')}
                    className="text-yellow-400/70 hover:text-yellow-400 transition-colors p-0.5 rounded-full hover:bg-yellow-400/10"
                    title="View definition"
                  >
                    <Info className="w-3.5 h-3.5" />
                  </button>
                </div>
                <span className="font-mono text-yellow-300">{Math.round(weights.freshness * 100)}%</span>
              </div>
              {activeTooltip === 'freshness' && (
                <div className="text-[11px] text-yellow-200 bg-yellow-400/10 p-2.5 rounded-lg border border-yellow-400/30 leading-relaxed font-sans mt-1">
                  {PARAMETER_DEFINITIONS.freshness}
                </div>
              )}
              <input
                type="range"
                min="0"
                max="100"
                value={Math.round(weights.freshness * 100)}
                onChange={(e) => handleSliderChange('freshness', Number(e.target.value))}
                className="w-full accent-yellow-400 h-2 bg-zinc-800 rounded-lg cursor-pointer"
              />
            </div>
          </div>
        </div>
      ) : (
        <div className="yellow-card p-5 space-y-3">
          <div className="flex items-center gap-2 text-yellow-400 font-bold text-xs uppercase tracking-wider font-mono">
            <Brain className="w-4 h-4 animate-pulse" />
            <span>PyTorch ML Model Active</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed font-sans">
            PyTorch RankNet neural network automatically computes optimal document relevance. Signal weights are calculated dynamically per query via SHAP attributions.
          </p>
        </div>
      )}
    </aside>
  );
}
