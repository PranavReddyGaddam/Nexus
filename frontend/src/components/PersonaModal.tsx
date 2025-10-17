import { X, Briefcase, MapPin, Award, TrendingUp } from 'lucide-react';

export interface Persona {
  id: string;
  name: string;
  title: string;
  location: string;
  industry: string;
  expertise: string[];
  experience: string;
  avatar?: string;
  bio: string;
  insights?: string[];
}

interface PersonaModalProps {
  persona: Persona | null;
  isOpen: boolean;
  onClose: () => void;
  onConsult?: (persona: Persona) => void;
}

export default function PersonaModal({ persona, isOpen, onClose, onConsult }: PersonaModalProps) {
  if (!isOpen || !persona) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.8)' }}
      onClick={onClose}
    >
      <div 
        className="bg-gray-900 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-gray-700 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="relative p-6 border-b border-gray-700">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
            aria-label="Close"
          >
            <X size={24} />
          </button>
          
          <div className="flex items-start gap-4">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold">
              {persona.avatar || persona.name.split(' ').map(n => n[0]).join('')}
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-white mb-1">{persona.name}</h2>
              <p className="text-blue-400 font-medium mb-2">{persona.title}</p>
              <div className="flex items-center gap-2 text-gray-400 text-sm">
                <MapPin size={16} />
                <span>{persona.location}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Industry & Experience */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center gap-2 text-blue-400 mb-2">
                <Briefcase size={18} />
                <span className="text-sm font-semibold">Industry</span>
              </div>
              <p className="text-white">{persona.industry}</p>
            </div>
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center gap-2 text-blue-400 mb-2">
                <Award size={18} />
                <span className="text-sm font-semibold">Experience</span>
              </div>
              <p className="text-white">{persona.experience}</p>
            </div>
          </div>

          {/* Bio */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-3">About</h3>
            <p className="text-gray-300 leading-relaxed">{persona.bio}</p>
          </div>

          {/* Expertise */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-3">Areas of Expertise</h3>
            <div className="flex flex-wrap gap-2">
              {persona.expertise.map((skill, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-blue-500 bg-opacity-20 text-blue-300 rounded-full text-sm border border-blue-500 border-opacity-30"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>

          {/* Insights */}
          {persona.insights && persona.insights.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <TrendingUp size={20} className="text-blue-400" />
                <h3 className="text-lg font-semibold text-white">Key Insights</h3>
              </div>
              <ul className="space-y-2">
                {persona.insights.map((insight, index) => (
                  <li key={index} className="flex items-start gap-2 text-gray-300">
                    <span className="text-blue-400 mt-1">•</span>
                    <span>{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Action Button */}
          <button
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-colors"
            onClick={(e) => {
              e.stopPropagation();
              if (onConsult && persona) onConsult(persona);
            }}
          >
            Consult {persona.name.split(' ')[0]} for Market Research
          </button>
        </div>
      </div>
    </div>
  );
}

