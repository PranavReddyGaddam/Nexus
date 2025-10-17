import React from 'react';
import { ChevronLeft, ChevronRight, Brain } from 'lucide-react';

interface AnalysisTabProps {
  isOpen: boolean;
  hasResults: boolean;
  onClick: () => void;
}

export default function AnalysisTab({ isOpen, hasResults, onClick }: AnalysisTabProps) {
  return (
    <button
      onClick={onClick}
      className={`
        fixed right-0 top-1/2 -translate-y-1/2 z-40
        ${isOpen ? 'translate-x-[384px]' : 'translate-x-0'}
        flex items-center gap-2
        bg-gray-900 text-white
        px-3 py-4 rounded-l-lg
        border-l border-y border-gray-700
        shadow-xl
        transition-transform duration-300
        hover:bg-gray-800
        group
      `}
      aria-label={isOpen ? 'Close Expert Analysis' : 'Open Expert Analysis'}
    >
      {/* Icon */}
      <div className={`transition-colors duration-300 ${hasResults ? 'text-blue-400' : 'text-gray-400'}`}>
        <Brain size={20} />
      </div>

      {/* Text (only shows on hover) */}
      <div className={`
        absolute right-full top-1/2 -translate-y-1/2
        whitespace-nowrap px-2 py-1
        bg-gray-800 rounded-md
        text-sm text-gray-300
        opacity-0 group-hover:opacity-100
        transition-opacity duration-200
        pointer-events-none
      `}>
        {isOpen ? 'Close Analysis' : 'Expert Analysis'}
        {hasResults && !isOpen && ' (Available)'}
      </div>

      {/* Arrow */}
      {isOpen ? (
        <ChevronRight size={16} className="text-gray-400" />
      ) : (
        <ChevronLeft size={16} className="text-gray-400" />
      )}
    </button>
  );
}
