import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import SidebarControls from './components/SidebarControls';
import TelemetryPanel from './components/TelemetryPanel';
import ResultCard from './components/ResultCard';
import ComparisonView from './components/ComparisonView';
import { GitCompare, AlertCircle, Brain, Terminal, Search } from 'lucide-react';

const DEFAULT_WEIGHTS = {
  semantic: 0.40,
  keyword: 0.25,
  authority: 0.20,
  freshness: 0.15,
};

export default function App() {
  const [activeTab, setActiveTab] = useState('search');
  const [query, setQuery] = useState('neural networks backpropagation');
  const [weights, setWeights] = useState(DEFAULT_WEIGHTS);
  const [activePreset, setActivePreset] = useState('Balanced');
  const [scoringMode, setScoringMode] = useState('manual');
  const [results, setResults] = useState([]);
  const [missingKeywords, setMissingKeywords] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showComparison, setShowComparison] = useState(false);

  useEffect(() => {
    executeSearch(query, weights, scoringMode);
  }, []);

  const executeSearch = async (searchQuery, activeWeights, mode = scoringMode) => {
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    setError(null);
    setMissingKeywords([]);

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchQuery,
          weights: activeWeights,
          scoring_mode: mode,
          limit: 10,
        }),
      });

      const responseText = await response.text();
      let data;
      try {
        data = JSON.parse(responseText);
      } catch (jsonErr) {
        if (!response.ok) {
          throw new Error('Server connection in progress...');
        }
        throw new Error('Server connection in progress...');
      }

      if (!response.ok) {
        throw new Error('Server connection in progress...');
      }

      setResults(data.results || []);
      setMissingKeywords(data.missing_keywords || []);
    } catch (err) {
      setError('Server connection in progress...');
      setResults([]);
      setMissingKeywords([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearchSubmit = (newQuery) => {
    executeSearch(newQuery, weights, scoringMode);
  };

  const handleWeightsApply = (newWeights, mode = scoringMode) => {
    executeSearch(query, newWeights, mode);
  };

  const handleCategorySelect = (catQuery) => {
    setQuery(catQuery);
    executeSearch(catQuery, weights, scoringMode);
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-slate-100 flex flex-col">
      <Header />

      {/* Navigation Tabs */}
      <div className="max-w-[1550px] w-full mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="flex space-x-2 border-b border-zinc-800 pb-px">
          <button
            onClick={() => setActiveTab('search')}
            className={`px-4 py-2 font-mono text-sm font-bold flex items-center gap-2 border-b-2 transition-colors ${
              activeTab === 'search'
                ? 'border-yellow-400 text-yellow-400'
                : 'border-transparent text-zinc-500 hover:text-zinc-300'
            }`}
          >
            <Search className="w-4 h-4" /> Vector Search
          </button>
        </div>
      </div>

      <main className="flex-1 max-w-[1550px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'search' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

            {/* Left Column: Controls (3 Cols) */}
            <div className="lg:col-span-3">
              <SidebarControls
                weights={weights}
                setWeights={setWeights}
                activePreset={activePreset}
                setActivePreset={setActivePreset}
                scoringMode={scoringMode}
                setScoringMode={setScoringMode}
                onApply={handleWeightsApply}
              />
            </div>

            {/* Center Column: Search Box & Results Feed (6 Cols) */}
            <div className="lg:col-span-6 space-y-6">
              {/* Search Box */}
              <div className="yellow-card p-5">
                <SearchBar
                  query={query}
                  setQuery={setQuery}
                  onSearch={handleSearchSubmit}
                  isLoading={isLoading}
                />
              </div>

              {/* Toolbar */}
              <div className="flex items-center justify-between border-b border-zinc-800 pb-3 font-mono">
                <div className="flex items-center gap-2">
                  <Terminal className="w-4 h-4 text-yellow-400" />
                  <span className="text-xs font-bold text-white uppercase tracking-wider">Search Ranks</span>
                  {results.length > 0 && (
                    <span className="text-xs px-2.5 py-0.5 rounded bg-zinc-900 text-yellow-300 border border-yellow-400/30 font-bold">
                      {results.length} documents
                    </span>
                  )}
                  {scoringMode === 'neural' && (
                    <span className="text-xs px-2.5 py-0.5 rounded bg-yellow-400/20 text-yellow-300 border border-yellow-400/40 font-bold flex items-center gap-1">
                      <Brain className="w-3.5 h-3.5 text-yellow-400" /> PyTorch Neural Re-Ranker
                    </span>
                  )}
                </div>

                <button
                  type="button"
                  onClick={() => setShowComparison(!showComparison)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-bold border flex items-center gap-1.5 transition-all ${
                    showComparison
                      ? 'bg-yellow-400/20 border-yellow-400 text-yellow-300 shadow-[0_0_12px_rgba(250,204,21,0.3)]'
                      : 'bg-zinc-900 border-zinc-800 text-slate-300 hover:border-yellow-400/40'
                  }`}
                >
                  <GitCompare className="w-3.5 h-3.5 text-yellow-400" />
                  <span>{showComparison ? 'Hide Matrix' : 'Comparison Matrix'}</span>
                </button>
              </div>

              {/* Comparison Matrix */}
              {showComparison && (
                <section>
                  <ComparisonView query={query} />
                </section>
              )}

              {/* Error Message */}
              {error && (
                <div className="yellow-card p-4 border-yellow-500/50 text-yellow-300 rounded-xl flex items-center gap-3 text-xs font-mono">
                  <AlertCircle className="w-5 h-5 text-yellow-400 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              {missingKeywords.length > 0 && (
                <div className="yellow-card p-4 border-amber-500/50 text-amber-200 rounded-xl flex items-start gap-3 text-xs font-mono">
                  <AlertCircle className="w-5 h-5 text-amber-400 shrink-0" />
                  <div>
                    <p className="font-bold">Keywords not found in the dataset</p>
                    <p className="mt-1 text-amber-100/80">{missingKeywords.join(', ')}</p>
                    {results.length > 0 && (
                      <p className="mt-1 text-zinc-400">Showing results using the query terms that were found.</p>
                    )}
                  </div>
                </div>
              )}

              {/* Results Feed */}
              <section className="space-y-4">
                {isLoading ? (
                  <div className="py-16 text-center space-y-3 font-mono yellow-card">
                    <div className="w-8 h-8 border-3 border-yellow-400 border-t-transparent rounded-full animate-spin mx-auto" />
                    <p className="text-xs text-yellow-300 font-bold tracking-wider">RETRIEVING & MULTI-SIGNAL RANKING CORA PAPERS...</p>
                  </div>
                ) : results.length > 0 ? (
                  results.map((item) => (
                    <ResultCard key={item.document_id} item={item} />
                  ))
                ) : (
                  <div className="yellow-card p-12 text-center space-y-2 font-mono">
                    <p className="text-yellow-300 font-bold text-sm">
                      {missingKeywords.length > 0
                        ? 'Keywords not found in the dataset.'
                        : 'No relevant results found for this query.'}
                    </p>
                    <p className="text-xs text-zinc-500">Try different keywords or adjust the ranking signals.</p>
                  </div>
                )}
              </section>
            </div>

            {/* Right Column: Telemetry & CORA Categories (3 Cols) */}
            <div className="lg:col-span-3">
              <TelemetryPanel onSelectCategory={handleCategorySelect} />
            </div>

          </div>
        )}

      </main>

      <footer className="border-t border-zinc-900 py-6 text-center text-xs text-zinc-500 font-mono">
        WhyRank.ai — Explainable Multi-Signal Information Retrieval System
      </footer>
    </div>
  );
}
