import React from 'react';
import LoadingSpinner from './LoadingSpinner';

interface LoadingOverlayProps {
  isVisible: boolean;
  message?: string;
}

export default function LoadingOverlay({ isVisible, message = 'Analyzing your idea with global experts...' }: LoadingOverlayProps) {
  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75 backdrop-blur-sm">
      <div className="bg-gray-900 rounded-2xl p-8 border border-gray-700 shadow-2xl max-w-md mx-4">
        <LoadingSpinner size="lg" text={message} />
        <div className="mt-4 text-center">
          <p className="text-gray-300 text-sm">
            This may take 10-30 seconds while our AI experts evaluate your idea
          </p>
        </div>
      </div>
    </div>
  );
}
