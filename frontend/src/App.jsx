import React, { useState } from 'react';

const CoralCard = ({ coral }) => (
  <div className="bg-white rounded-xl shadow-lg hover:shadow-2xl transition-shadow p-6 border border-marine-100 flex flex-col h-full">
    <div className="flex justify-between items-start mb-4">
      <h3 className="text-xl font-bold text-marine-900 leading-tight">{coral.species_name}</h3>
      <span className="bg-marine-100 text-marine-700 text-xs font-semibold px-2 py-1 rounded-full whitespace-nowrap">
        {Math.round(coral.score * 100)}% Match
      </span>
    </div>
    
    <div className="space-y-3 mb-6 flex-grow">
      <p className="text-sm text-gray-700 italic">"{coral.description.substring(0, 160)}..."</p>
      
      <div className="flex flex-wrap gap-2">
        {coral.color && (
          <span className="bg-blue-50 text-blue-600 text-[10px] uppercase tracking-wider font-bold px-2 py-1 rounded border border-blue-100">
            {coral.color}
          </span>
        )}
        {coral.habitat && (
          <span className="bg-teal-50 text-teal-600 text-[10px] uppercase tracking-wider font-bold px-2 py-1 rounded border border-teal-100">
            {coral.habitat}
          </span>
        )}
      </div>
    </div>
    
    <div className="pt-4 border-t border-gray-100 mt-auto">
      <p className="text-xs text-gray-500 font-medium">Abundance: <span className="text-gray-700">{coral.abundance}</span></p>
    </div>
  </div>
);

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/api/search/?q=${encodeURIComponent(query)}`);
      if (!response.ok) throw new Error('Failed to fetch results');
      const data = await response.json();
      setResults(data.results);
    } catch (err) {
      setError('Connection to backend failed. Ensure Django server is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-marine-50 font-sans text-gray-900">
      {/* Hero / Search Section */}
      <header className="bg-marine-900 text-white py-16 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-extrabold mb-4 tracking-tight">🪸 CoralMorph Search</h1>
          <p className="text-marine-200 text-lg mb-8 max-w-2xl mx-auto">
            Discover coral species using natural language. Our semantic engine understands morphological traits, habitats, and color descriptions.
          </p>
          
          <form onSubmit={handleSearch} className="relative max-w-2xl mx-auto">
            <input
              type="text"
              className="w-full py-4 px-6 rounded-full text-gray-900 text-lg shadow-2xl focus:ring-4 focus:ring-marine-400 focus:outline-none pr-32"
              placeholder="e.g., spiky green branches in shallow water"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading}
              className="absolute right-2 top-2 bottom-2 bg-marine-600 hover:bg-marine-500 text-white font-bold px-8 rounded-full transition-colors disabled:bg-gray-400"
            >
              {loading ? 'Searching...' : 'Explore'}
            </button>
          </form>
        </div>
      </header>

      {/* Main Results Section */}
      <main className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8 text-red-700">
            <p className="font-bold">Error</p>
            <p>{error}</p>
          </div>
        )}

        {results.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {results.map((coral, idx) => (
              <CoralCard key={idx} coral={coral} />
            ))}
          </div>
        ) : !loading && !error && (
          <div className="text-center py-20 opacity-50">
            <div className="text-6xl mb-4">🌊</div>
            <p className="text-xl">Enter a description above to start exploring the reef.</p>
          </div>
        )}
      </main>
      
      <footer className="py-8 text-center text-gray-400 text-sm">
        Built with DuckDB & Sentence-Transformers • Semantic Search Prototype
      </footer>
    </div>
  );
}

export default App;
