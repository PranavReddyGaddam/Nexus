import React, { useState, useEffect } from 'react';
import { X, Mic, MicOff, Video, VideoOff, Phone, PhoneOff, Volume2, VolumeX } from 'lucide-react';
import type { Persona } from './PersonaModal';

interface CallScreenProps {
  persona: Persona;
  isOpen: boolean;
  onClose: () => void;
  onCallEnd: () => void;
}

export default function CallScreen({ persona, isOpen, onClose, onCallEnd }: CallScreenProps) {
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOn, setIsVideoOn] = useState(true);
  const [isSpeakerOn, setIsSpeakerOn] = useState(true);
  const [callDuration, setCallDuration] = useState(0);
  const [callStatus, setCallStatus] = useState<'connecting' | 'connected' | 'ended'>('connecting');

  // Timer for call duration
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (callStatus === 'connected') {
      interval = setInterval(() => {
        setCallDuration(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [callStatus]);

  // Simulate call connection
  useEffect(() => {
    if (isOpen) {
      setCallStatus('connecting');
      // Simulate connection delay
      setTimeout(() => {
        setCallStatus('connected');
      }, 2000);
    }
  }, [isOpen]);

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleEndCall = () => {
    setCallStatus('ended');
    setTimeout(() => {
      onCallEnd();
      onClose();
    }, 1000);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-10 bg-black bg-opacity-50 backdrop-blur-sm">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center">
              <span className="text-white font-semibold text-lg">
                {persona.name.split(' ').map(n => n[0]).join('')}
              </span>
            </div>
            <div>
              <h2 className="text-white font-semibold text-lg">{persona.name}</h2>
              <p className="text-gray-300 text-sm">{persona.title}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:text-gray-300 transition-colors"
          >
            <X size={24} />
          </button>
        </div>
      </div>

      {/* Main Call Area */}
      <div className="flex h-full">
        {/* Video Area */}
        <div className="flex-1 relative bg-gray-900">
          {/* Expert Video (placeholder) */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-64 h-64 bg-gray-800 rounded-lg flex items-center justify-center">
              <div className="w-32 h-32 bg-purple-600 rounded-full flex items-center justify-center">
                <span className="text-white font-semibold text-4xl">
                  {persona.name.split(' ').map(n => n[0]).join('')}
                </span>
              </div>
            </div>
          </div>

          {/* Call Status Overlay */}
          <div className="absolute top-20 left-1/2 transform -translate-x-1/2">
            <div className="bg-black bg-opacity-50 backdrop-blur-sm rounded-lg px-4 py-2">
              {callStatus === 'connecting' && (
                <div className="flex items-center space-x-2 text-white">
                  <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                  <span>Connecting...</span>
                </div>
              )}
              {callStatus === 'connected' && (
                <div className="flex items-center space-x-2 text-white">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span>Connected • {formatDuration(callDuration)}</span>
                </div>
              )}
              {callStatus === 'ended' && (
                <div className="flex items-center space-x-2 text-white">
                  <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                  <span>Call Ended</span>
                </div>
              )}
            </div>
          </div>

          {/* Your Video (small overlay) */}
          <div className="absolute bottom-4 right-4 w-32 h-24 bg-gray-800 rounded-lg border-2 border-gray-600">
            <div className="w-full h-full flex items-center justify-center">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-semibold">You</span>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar with Persona Info */}
        <div className="w-80 bg-gray-900 border-l border-gray-700 p-6 overflow-y-auto">
          <div className="space-y-6">
            {/* Persona Details */}
            <div>
              <h3 className="text-white font-semibold text-lg mb-3">Expert Profile</h3>
              <div className="space-y-3">
                <div className="bg-gray-800 rounded-lg p-3">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold">
                        {persona.name.split(' ').map(n => n[0]).join('')}
                      </span>
                    </div>
                    <div>
                      <p className="text-white font-medium">{persona.name}</p>
                      <p className="text-gray-400 text-sm">{persona.title}</p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-gray-800 rounded-lg p-3">
                  <p className="text-gray-400 text-sm mb-1">Location</p>
                  <p className="text-white">{persona.location}</p>
                </div>
                
                <div className="bg-gray-800 rounded-lg p-3">
                  <p className="text-gray-400 text-sm mb-1">Industry</p>
                  <p className="text-white">{persona.industry}</p>
                </div>
                
                <div className="bg-gray-800 rounded-lg p-3">
                  <p className="text-gray-400 text-sm mb-1">Experience</p>
                  <p className="text-white">{persona.experience}</p>
                </div>
              </div>
            </div>

            {/* Expertise */}
            <div>
              <h4 className="text-white font-medium mb-2">Areas of Expertise</h4>
              <div className="flex flex-wrap gap-2">
                {persona.expertise.map((skill, index) => (
                  <span
                    key={index}
                    className="bg-blue-600 text-white text-xs px-2 py-1 rounded-full"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Key Insights */}
            {persona.insights && (
              <div>
                <h4 className="text-white font-medium mb-2">Key Insights</h4>
                <ul className="space-y-2">
                  {persona.insights.map((insight, index) => (
                    <li key={index} className="text-gray-300 text-sm flex items-start">
                      <span className="text-blue-400 mr-2">•</span>
                      {insight}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Call Controls */}
      <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 backdrop-blur-sm">
        <div className="flex items-center justify-center space-x-4 p-6">
          {/* Mute Button */}
          <button
            onClick={() => setIsMuted(!isMuted)}
            className={`w-12 h-12 rounded-full flex items-center justify-center transition-colors ${
              isMuted ? 'bg-red-600 hover:bg-red-700' : 'bg-gray-700 hover:bg-gray-600'
            }`}
          >
            {isMuted ? <MicOff size={20} className="text-white" /> : <Mic size={20} className="text-white" />}
          </button>

          {/* Video Button */}
          <button
            onClick={() => setIsVideoOn(!isVideoOn)}
            className={`w-12 h-12 rounded-full flex items-center justify-center transition-colors ${
              !isVideoOn ? 'bg-red-600 hover:bg-red-700' : 'bg-gray-700 hover:bg-gray-600'
            }`}
          >
            {isVideoOn ? <Video size={20} className="text-white" /> : <VideoOff size={20} className="text-white" />}
          </button>

          {/* Speaker Button */}
          <button
            onClick={() => setIsSpeakerOn(!isSpeakerOn)}
            className={`w-12 h-12 rounded-full flex items-center justify-center transition-colors ${
              isSpeakerOn ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-600 hover:bg-gray-500'
            }`}
          >
            {isSpeakerOn ? <Volume2 size={20} className="text-white" /> : <VolumeX size={20} className="text-white" />}
          </button>

          {/* End Call Button */}
          <button
            onClick={handleEndCall}
            className="w-14 h-14 bg-red-600 hover:bg-red-700 rounded-full flex items-center justify-center transition-colors"
          >
            <PhoneOff size={24} className="text-white" />
          </button>
        </div>
      </div>
    </div>
  );
}
