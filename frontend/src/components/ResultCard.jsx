import React, { useState } from 'react';
import { ExternalLink, CheckCircle2, Tag, ChevronDown, ChevronUp, Sparkles, Layers, ShieldCheck, Clock, Terminal } from 'lucide-react';

export default function ResultCard({ item }) {
  const [showExplanation, setShowExplanation] = useState(true);

  const { rank, title, url, snippet, scores, contributions, explanation } = item;
  const finalScorePercent = (scores.final * 100).toFixed(1);

  return (
    <div className="yellow-card p-6 transition-all duration-300 space-y-5">
      {/* Header Row */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-4">
          {/* Rank Badge */}
          <div className="w-11 h-11 rounded-xl bg-yellow-400 text-black font-mono font-black text-base flex items-center justify-center shadow-[0_0_15px_rgba(250,204,21,0.4)] shrink-0 border border-yellow-300">
            #{rank < 10 ? `0${rank}` : rank}
          </div>

          <div className="space-y-1">
            <a
              href={url || '#'}
              target="_blank"
              rel="noopener noreferrer"
              className="text-base font-extrabold text-white hover:text-yellow-300 transition-colors flex items-center gap-2 group font-sans tracking-tight leading-snug"
            >
              <span>{title}</span>
              <ExternalLink className="w-4 h-4 text-yellow-400 opacity-70 group-hover:opacity-100 transition-opacity" />
            </a>
            {url && <span className="text-xs text-zinc-400 font-mono truncate max-w-lg block">{url}</span>}
          </div>
        </div>

        {/* Final Score Pill */}
        <div className="flex flex-col items-end shrink-0">
          <span className="text-[10px] uppercase font-mono font-bold text-zinc-400 tracking-wider">Final Score</span>
          <span className="text-xl font-black font-mono text-yellow-300 bg-yellow-400/10 px-3 py-1 rounded-xl border border-yellow-400/40 shadow-inner">
            {finalScorePercent}%
          </span>
        </div>
      </div>

      {/* Snippet */}
      {snippet && (
        <p className="text-xs text-slate-300 leading-relaxed black-inset p-3.5 rounded-xl font-mono">
          {snippet}
        </p>
      )}

      {/* Signals Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
        {/* Semantic */}
        <div className="black-inset p-3 rounded-xl space-y-1.5">
          <div className="flex justify-between items-center text-[11px]">
            <span className="text-yellow-400 font-bold flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5" /> Vector
            </span>
            <span className="font-bold text-yellow-300">{Math.round(scores.semantic * 100)}%</span>
          </div>
          <div className="w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-yellow-400 h-full rounded-full transition-all duration-500 shadow-[0_0_8px_#facc15]"
              style={{ width: `${scores.semantic * 100}%` }}
            />
          </div>
          <div className="text-[10px] text-zinc-400 text-right">
            +{(contributions.semantic * 100).toFixed(1)}%
          </div>
        </div>

        {/* BM25 */}
        <div className="black-inset p-3 rounded-xl space-y-1.5">
          <div className="flex justify-between items-center text-[11px]">
            <span className="text-yellow-400 font-bold flex items-center gap-1">
              <Layers className="w-3.5 h-3.5" /> BM25
            </span>
            <span className="font-bold text-yellow-300">{Math.round(scores.keyword * 100)}%</span>
          </div>
          <div className="w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-yellow-400 h-full rounded-full transition-all duration-500 shadow-[0_0_8px_#facc15]"
              style={{ width: `${scores.keyword * 100}%` }}
            />
          </div>
          <div className="text-[10px] text-zinc-400 text-right">
            +{(contributions.keyword * 100).toFixed(1)}%
          </div>
        </div>

        {/* PageRank */}
        <div className="black-inset p-3 rounded-xl space-y-1.5">
          <div className="flex justify-between items-center text-[11px]">
            <span className="text-yellow-400 font-bold flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" /> PageRank
            </span>
            <span className="font-bold text-yellow-300">{Math.round(scores.authority * 100)}%</span>
          </div>
          <div className="w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-yellow-400 h-full rounded-full transition-all duration-500 shadow-[0_0_8px_#facc15]"
              style={{ width: `${scores.authority * 100}%` }}
            />
          </div>
          <div className="text-[10px] text-zinc-400 text-right">
            +{(contributions.authority * 100).toFixed(1)}%
          </div>
        </div>

        {/* Freshness */}
        <div className="black-inset p-3 rounded-xl space-y-1.5">
          <div className="flex justify-between items-center text-[11px]">
            <span className="text-yellow-400 font-bold flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" /> Freshness
            </span>
            <span className="font-bold text-yellow-300">{Math.round(scores.freshness * 100)}%</span>
          </div>
          <div className="w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-yellow-400 h-full rounded-full transition-all duration-500 shadow-[0_0_8px_#facc15]"
              style={{ width: `${scores.freshness * 100}%` }}
            />
          </div>
          <div className="text-[10px] text-zinc-400 text-right">
            +{(contributions.freshness * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* WHY Explanation Accordion */}
      <div className="border-t border-zinc-800 pt-3 font-mono">
        <button
          type="button"
          onClick={() => setShowExplanation(!showExplanation)}
          className="flex items-center justify-between w-full text-xs font-bold text-yellow-400 hover:text-yellow-300 transition-colors uppercase tracking-wider"
        >
          <span className="flex items-center gap-1.5">
            <Terminal className="w-3.5 h-3.5" />
            <span>Ranking Explanation & Feature Attribution</span>
          </span>
          {showExplanation ? <ChevronUp className="w-4 h-4 text-yellow-400" /> : <ChevronDown className="w-4 h-4 text-yellow-400" />}
        </button>

        {showExplanation && (
          <div className="mt-2.5 space-y-2.5 black-inset p-4 rounded-xl text-xs">
            {/* Positive Factors */}
            {explanation.positive_factors && explanation.positive_factors.length > 0 && (
              <div className="space-y-1.5">
                {explanation.positive_factors.map((factor, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-slate-200">
                    <CheckCircle2 className="w-4 h-4 text-yellow-400 shrink-0" />
                    <span className="font-mono text-slate-200">{factor}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Matched Terms */}
            {explanation.matched_terms && explanation.matched_terms.length > 0 && (
              <div className="flex items-center gap-1.5 flex-wrap pt-2 border-t border-zinc-800">
                <span className="text-[11px] text-zinc-400 font-mono flex items-center gap-1 font-bold">
                  <Tag className="w-3 h-3 text-yellow-400" /> Matched Terms:
                </span>
                {explanation.matched_terms.map((term, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 rounded bg-yellow-400/20 text-yellow-300 border border-yellow-400/40 font-mono text-[10px] font-bold shadow-[0_0_8px_rgba(250,204,21,0.2)]"
                  >
                    {term}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
