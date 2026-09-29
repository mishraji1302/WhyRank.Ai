import React from 'react';
import { X, Terminal, Zap } from 'lucide-react';

const EXAMPLE_QUERIES = [
  "neural networks backpropagation",
  "reinforcement learning policy gradient",
  "probabilistic methods bayesian inference",
  "genetic algorithms crossover",
  "case based reasoning similarity",
];

export default function SearchBar({ query, setQuery, onSearch, isLoading }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
    }
  };

  const handleSelectExample = (sampleQuery) => {
    setQuery(sampleQuery);
    onSearch(sampleQuery);
  };

  return (
    <div className="w-full space-y-3.5 font-mono">
      <form onSubmit={handleSubmit} className="relative flex items-center">
        <div className="absolute left-4 text-yellow-400 pointer-events-none">
          <Terminal className="w-5 h-5" />
        </div>

        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter search query across 2,708 CORA Machine Learning papers..."
          className="w-full pl-12 pr-32 py-4 bg-black text-yellow-300 placeholder-zinc-500 rounded-xl border border-yellow-500/40 focus:outline-none focus:border-yellow-400 focus:shadow-[0_0_20px_rgba(250,204,21,0.35)] transition-all font-mono text-sm shadow-inner"
        />

        {query && (
          <button
            type="button"
            onClick={() => setQuery('')}
            className="absolute right-32 text-zinc-400 hover:text-yellow-400 p-1 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}

        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="absolute right-2 px-5 py-2.5 bg-yellow-400 hover:bg-yellow-300 text-black font-mono font-black text-xs uppercase tracking-wider rounded-lg shadow-[0_0_15px_rgba(250,204,21,0.4)] disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
        >
          {isLoading ? (
            <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin" />
          ) : (
            <>
              <Zap className="w-3.5 h-3.5 fill-current" />
              <span>Query</span>
            </>
          )}
        </button>
      </form>

      {/* Quick Queries */}
      <div className="flex items-center gap-2 flex-wrap text-xs">
        <span className="text-zinc-400 font-mono text-[11px] flex items-center gap-1">
          <span className="text-yellow-400">&gt;</span> Quick Queries:
        </span>
        {EXAMPLE_QUERIES.map((sample, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => handleSelectExample(sample)}
            className="px-2.5 py-1 rounded-md bg-zinc-900 hover:bg-zinc-800 text-yellow-300/90 hover:text-yellow-200 border border-yellow-500/20 hover:border-yellow-400/50 transition-all font-mono text-[11px]"
          >
            {sample}
          </button>
        ))}
      </div>
    </div>
  );
}
