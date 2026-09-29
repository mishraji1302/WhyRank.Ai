import React, { useState, useEffect } from 'react';
import { GitCompare } from 'lucide-react';

const PROFILE_A_WEIGHTS = { semantic: 0.40, keyword: 0.25, authority: 0.20, freshness: 0.15 }; // Balanced
const PROFILE_B_WEIGHTS = { semantic: 0.00, keyword: 1.00, authority: 0.00, freshness: 0.00 }; // Pure Keyword

async function safePost(url, payload) {
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const text = await res.text();
    if (!res.ok) return { results: [] };
    return JSON.parse(text);
  } catch (e) {
    return { results: [] };
  }
}

export default function ComparisonView({ query }) {
  const [resultsA, setResultsA] = useState([]);
  const [resultsB, setResultsB] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!query) return;
    fetchComparisonData();
  }, [query]);

  const fetchComparisonData = async () => {
    setLoading(true);
    try {
      const [resA, resB] = await Promise.all([
        safePost('/api/search', { query, weights: PROFILE_A_WEIGHTS, limit: 5 }),
        safePost('/api/search', { query, weights: PROFILE_B_WEIGHTS, limit: 5 }),
      ]);

      setResultsA(resA.results || []);
      setResultsB(resB.results || []);
    } catch (e) {
      console.error("Comparison fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  if (!query) return null;

  return (
    <div className="yellow-card p-5 space-y-4 font-mono">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div className="flex items-center gap-2">
          <GitCompare className="w-5 h-5 text-yellow-400" />
          <h3 className="font-bold text-white text-sm uppercase tracking-wider text-glow-yellow">Ranking Comparison Matrix</h3>
        </div>
        <span className="text-[11px] text-zinc-400">Comparing result ordering under 2 profiles</span>
      </div>

      {loading ? (
        <div className="py-8 text-center text-zinc-400 text-xs font-mono">Computing comparison matrix ranks...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Profile A: Balanced */}
          <div className="black-inset p-4 rounded-xl space-y-3">
            <div className="flex justify-between items-center border-b border-zinc-800 pb-2">
              <span className="font-extrabold text-xs text-yellow-400 uppercase tracking-wider">Profile A: Balanced</span>
              <span className="text-[10px] text-zinc-400">Sem 40% | KW 25% | Auth 20% | Fresh 15%</span>
            </div>
            <div className="space-y-2">
              {resultsA.map((item) => (
                <div key={item.document_id} className="bg-zinc-900 p-2.5 rounded-lg border border-zinc-800 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2 max-w-[80%]">
                    <span className="font-bold text-yellow-400 font-mono">#{item.rank}</span>
                    <span className="text-slate-200 truncate font-sans">{item.title}</span>
                  </div>
                  <span className="font-mono text-[11px] text-yellow-300 font-bold">{(item.scores.final * 100).toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Profile B: Pure Keyword */}
          <div className="black-inset p-4 rounded-xl space-y-3">
            <div className="flex justify-between items-center border-b border-zinc-800 pb-2">
              <span className="font-extrabold text-xs text-yellow-400 uppercase tracking-wider">Profile B: Keyword First</span>
              <span className="text-[10px] text-zinc-400">Sem 0% | KW 100% | Auth 0% | Fresh 0%</span>
            </div>
            <div className="space-y-2">
              {resultsB.map((item) => (
                <div key={item.document_id} className="bg-zinc-900 p-2.5 rounded-lg border border-zinc-800 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2 max-w-[80%]">
                    <span className="font-bold text-yellow-400 font-mono">#{item.rank}</span>
                    <span className="text-slate-200 truncate font-sans">{item.title}</span>
                  </div>
                  <span className="font-mono text-[11px] text-yellow-300 font-bold">{(item.scores.final * 100).toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
