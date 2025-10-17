import React, { useEffect } from 'react';
import { X, TrendingUp, AlertCircle, Lightbulb, MapPin, Brain } from 'lucide-react';
import type { Persona } from './PersonaModal';

interface PersonaRating {
  persona: Persona;
  rating: number; // 0-10
  sentiment: 'positive' | 'neutral' | 'cautious';
  keyInsight: string;
}

type FocusOpts = {
  highlight?: boolean;      // highlight the pin
  spinIntoView?: boolean;   // animate camera to the point
};

type Coords = { lat: number; lng: number };

interface ResultsSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  startupIdea: string;
  results: PersonaRating[];
  onPersonaClick: (persona: Persona) => void;

  /** NEW: parent passes this so the globe can focus/spin to a persona's location */
  onFocusLocation: (coords: Coords, opts?: FocusOpts) => void;
}

export default function ResultsSidebar({ 
  isOpen, 
  onClose, 
  startupIdea, 
  results,
  onPersonaClick,
  onFocusLocation,
}: ResultsSidebarProps) {
  // Map a location string -> coords. Replace with your real mapper if available.
  const locationToCoords = (loc?: string): Coords | null => {
    if (!loc) return null;
    const L = loc.toLowerCase();
    if (L.includes('new york'))  return { lat: 40.7128,  lng: -74.0060 };
    if (L.includes('london'))    return { lat: 51.5074,  lng: -0.1278 };
    if (L.includes('tokyo'))     return { lat: 35.6895,  lng: 139.6917 };
    if (L.includes('hong kong')) return { lat: 22.3193,  lng: 114.1694 };
    if (L.includes('singapore')) return { lat: 1.3521,   lng: 103.8198 };
    if (L.includes('shanghai'))  return { lat: 31.2304,  lng: 121.4737 };
    if (L.includes('frankfurt')) return { lat: 50.1109,  lng: 8.6821 };
    if (L.includes('paris'))     return { lat: 48.8566,  lng: 2.3522 };
    if (L.includes('zurich'))    return { lat: 47.3769,  lng: 8.5417 };
    if (L.includes('toronto'))   return { lat: 43.6532,  lng: -79.3832 };
    if (L.includes('sydney'))    return { lat: -33.8688, lng: 151.2093 };
    if (L.includes('mumbai'))    return { lat: 19.0760,  lng: 72.8777 };
    if (L.includes('dubai'))     return { lat: 25.276987,lng: 55.296249 };
    if (L.includes('seoul'))     return { lat: 37.5665,  lng: 126.9780 };
    return null;
  };

  // When the sidebar opens and has results, focus the top persona's location
  useEffect(() => {
    if (!isOpen || results.length === 0) return;
    const top = results[0]?.persona as Persona & Partial<Coords>;
    const coords =
      (typeof top?.lat === 'number' && typeof top?.lng === 'number')
        ? { lat: top.lat, lng: top.lng }
        : locationToCoords(top?.location);

    if (coords) {
      onFocusLocation(coords, { highlight: true, spinIntoView: true });
    }
  }, [isOpen, results, onFocusLocation]);

  // Show placeholder if sidebar is open but no results yet
  if (!results.length) {
    return isOpen ? (
      <div 
        className={`
          fixed right-0 top-0 bottom-0 z-40
          w-96 bg-gray-900 border-l border-gray-700 shadow-2xl
          transform transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : 'translate-x-full'}
          overflow-hidden flex flex-col
        `}
      >
        <div className="flex-shrink-0 bg-gray-900 border-b border-gray-700 p-4">
          <div className="flex items-start justify-between mb-3">
            <h2 className="text-xl font-bold text-white">Expert Analysis</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white transition-colors"
              aria-label="Close"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
          <div className="w-16 h-16 mb-4 rounded-full bg-gray-800 border-2 border-gray-700 flex items-center justify-center">
            <Brain size={32} className="text-gray-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-300 mb-2">
            No Analysis Yet
          </h3>
          <p className="text-gray-500 text-sm max-w-xs">
            Enter your startup idea in the chat below and our expert personas will provide detailed feedback and insights.
          </p>
        </div>
      </div>
    ) : null;
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-400 bg-green-500/20 border-green-500/30';
      case 'neutral':  return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
      case 'cautious': return 'text-orange-400 bg-orange-500/20 border-orange-500/30';
      default:         return 'text-gray-400 bg-gray-500/20 border-gray-500/30';
    }
  };

  const getRatingColor = (rating: number) => {
    if (rating >= 8) return 'text-green-400';
    if (rating >= 6) return 'text-blue-400';
    if (rating >= 4) return 'text-yellow-400';
    return 'text-orange-400';
  };

  const averageRating = results.length > 0 
    ? (results.reduce((sum, r) => sum + r.rating, 0) / results.length).toFixed(1)
    : '0.0';

  return (
    <div 
      className={`
        fixed right-0 top-0 bottom-0 z-40
        w-96 bg-gray-900 border-l border-gray-700 shadow-2xl
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : 'translate-x-full'}
        overflow-hidden flex flex-col
      `}
    >
      {/* Header */}
      <div className="flex-shrink-0 bg-gray-900 border-b border-gray-700 p-4">
        <div className="flex items-start justify-between mb-3">
          <h2 className="text-xl font-bold text-white">Expert Analysis</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
            aria-label="Close"
          >
            <X size={24} />
          </button>
        </div>
        
        {/* Idea Summary */}
        <div className="bg-gray-800 rounded-lg p-3 mb-3">
          <p className="text-sm text-gray-400 mb-1">Your Idea:</p>
          <p className="text-white text-sm line-clamp-2">{startupIdea}</p>
        </div>

        {/* Overall Rating */}
        <div className="flex items-center justify-between bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
          <div className="flex items-center gap-2">
            <TrendingUp size={20} className="text-blue-400" />
            <span className="text-sm text-gray-300">Overall Score</span>
          </div>
          <span className="text-2xl font-bold text-blue-400">{averageRating}/10</span>
        </div>
      </div>

      {/* Results List - Scrollable */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        <div className="flex items-center gap-2 mb-2">
          <Lightbulb size={18} className="text-yellow-400" />
          <h3 className="text-sm font-semibold text-white">
            {results.length} Experts Consulted
          </h3>
        </div>

        {results.map((result) => (
          <div
            key={result.persona.id}
            className="bg-gray-800 rounded-lg border border-gray-700 hover:border-blue-500/50 transition-all cursor-pointer"
            onClick={() => {
              onPersonaClick(result.persona);
              // Also focus the globe on this persona’s location
              const p = result.persona as Persona & Partial<Coords>;
              const coords =
                (typeof p.lat === 'number' && typeof p.lng === 'number')
                  ? { lat: p.lat, lng: p.lng }
                  : locationToCoords(p.location);
              if (coords) {
                onFocusLocation(coords, { highlight: true, spinIntoView: true });
              }
            }}
          >
            <div className="p-4">
              {/* Persona Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold">
                      {result.persona.name.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div>
                      <h4 className="text-white font-semibold text-sm">
                        {result.persona.name}
                      </h4>
                      <p className="text-xs text-gray-400">{result.persona.title}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-1 text-xs text-gray-400 ml-10">
                    <MapPin size={12} />
                    <span>{result.persona.location}</span>
                  </div>
                </div>

                {/* Rating Badge */}
                <div className="flex flex-col items-end">
                  <div className={`text-2xl font-bold ${getRatingColor(result.rating)}`}>
                    {result.rating}
                  </div>
                  <div className="text-xs text-gray-500">/ 10</div>
                </div>
              </div>

              {/* Sentiment Badge */}
              <div className="mb-3">
                <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs border ${getSentimentColor(result.sentiment)}`}>
                  {result.sentiment === 'positive' && '✓'}
                  {result.sentiment === 'neutral' && '−'}
                  {result.sentiment === 'cautious' && '!'}
                  <span className="capitalize">{result.sentiment}</span>
                </span>
              </div>

              {/* Industry Tag */}
              <div className="mb-3">
                <span className="inline-block px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs border border-blue-500/30">
                  {result.persona.industry}
                </span>
              </div>

              {/* Key Insight */}
              <div className="bg-gray-900/50 rounded p-2 border border-gray-700">
                <div className="flex items-start gap-2">
                  <AlertCircle size={14} className="text-blue-400 mt-0.5 flex-shrink-0" />
                  <p className="text-xs text-gray-300 leading-relaxed">
                    {result.keyInsight}
                  </p>
                </div>
              </div>

              {/* View Details Link */}
              <button className="mt-3 text-xs text-blue-400 hover:text-blue-300 transition-colors w-full text-right">
                View Full Analysis →
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
