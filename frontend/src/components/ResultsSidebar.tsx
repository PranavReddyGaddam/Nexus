import { X, TrendingUp, AlertCircle, Lightbulb, MapPin } from 'lucide-react';
import type { Persona } from './PersonaModal';

interface PersonaRating {
  persona: Persona;
  rating: number; // 0-10
  sentiment: 'positive' | 'neutral' | 'cautious';
  keyInsight: string;
}

interface ResultsSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  startupIdea: string;
  results: PersonaRating[];
  onPersonaClick: (persona: Persona) => void;
}

export default function ResultsSidebar({ 
  isOpen, 
  onClose, 
  startupIdea, 
  results,
  onPersonaClick 
}: ResultsSidebarProps) {
  if (!isOpen) return null;

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-400 bg-green-500/20 border-green-500/30';
      case 'neutral': return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
      case 'cautious': return 'text-orange-400 bg-orange-500/20 border-orange-500/30';
      default: return 'text-gray-400 bg-gray-500/20 border-gray-500/30';
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
    <div className="fixed right-0 top-0 h-screen w-96 bg-gray-900 border-l border-gray-700 shadow-2xl z-50 overflow-y-auto">
      {/* Header */}
      <div className="sticky top-0 bg-gray-900 border-b border-gray-700 p-4 z-10">
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

      {/* Results List */}
      <div className="p-4 space-y-3">
        <div className="flex items-center gap-2 mb-2">
          <Lightbulb size={18} className="text-yellow-400" />
          <h3 className="text-sm font-semibold text-white">
            {results.length} Experts Consulted
          </h3>
        </div>

        {results.map((result, index) => (
          <div
            key={result.persona.id}
            className="bg-gray-800 rounded-lg border border-gray-700 hover:border-blue-500/50 transition-all cursor-pointer"
            onClick={() => onPersonaClick(result.persona)}
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

      {/* Footer */}
      <div className="sticky bottom-0 bg-gray-900 border-t border-gray-700 p-4">
        <button 
          onClick={onClose}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-colors"
        >
          Refine Idea & Get More Feedback
        </button>
      </div>
    </div>
  );
}

