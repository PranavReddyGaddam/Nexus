import { useEffect, useState, useRef } from 'react';
import { X, Mic, MicOff, Phone, PhoneOff } from 'lucide-react';
import { Conversation } from '@elevenlabs/client';

interface VoiceCallModalProps {
  isOpen: boolean;
  onClose: () => void;
  agentId: string;
  personaName: string;
  consultationId: number;
}

export default function VoiceCallModal({
  isOpen,
  onClose,
  agentId,
  personaName,
  consultationId
}: VoiceCallModalProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [isCallActive, setIsCallActive] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [status, setStatus] = useState<string>('Initializing...');
  const [error, setError] = useState<string | null>(null);
  
  const conversationRef = useRef<Conversation | null>(null);
  const conversationIdRef = useRef<string | null>(null);
  const isInitializingRef = useRef<boolean>(false);
  const isCleaningUpRef = useRef<boolean>(false);
  const hasInitializedRef = useRef<boolean>(false);

  // Effect to handle conversation lifecycle based on isOpen
  useEffect(() => {
    console.log('[VoiceCall] isOpen changed to:', isOpen);
    
    if (isOpen) {
      // Modal opened - start conversation
      startConversation();
    } else {
      // Modal closed - cleanup conversation
      cleanupConversation();
    }
    
    // Cleanup on unmount
    return () => {
      console.log('[VoiceCall] Component unmounting');
      cleanupConversation();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);
  
  const startConversation = async () => {
    // Prevent multiple initializations
    if (conversationRef.current || isInitializingRef.current || isCleaningUpRef.current) {
      console.log('[VoiceCall] Already have conversation or initializing/cleaning, skipping');
      return;
    }
    
    // Prevent React StrictMode double initialization
    if (hasInitializedRef.current && conversationRef.current) {
      console.log('[VoiceCall] Already initialized in this render cycle');
      return;
    }

    try {
      isInitializingRef.current = true;
      hasInitializedRef.current = true;
      setStatus('Connecting to expert...');
      console.log('[VoiceCall] Starting session for agent:', agentId);
      console.log('[VoiceCall] Current conversation ref:', conversationRef.current);
        
      // Initialize ElevenLabs conversation - SDK handles microphone internally
      const conversation = await Conversation.startSession({
        agentId: agentId,
        onConnect: () => {
          console.log('[VoiceCall] Connected to ElevenLabs');
          setIsConnected(true);
          setIsCallActive(true);
          setStatus('Connected');
        },
        onDisconnect: () => {
          console.log('[VoiceCall] Disconnected from ElevenLabs');
          setIsConnected(false);
          setIsCallActive(false);
          setStatus('Disconnected');
        },
        onMessage: (message: any) => {
          // Message handler - not used for transcript
          console.log('[VoiceCall] Message received:', message.type);
        },
        onError: (error: any) => {
          console.error('[VoiceCall] Error:', error);
          setError(error?.message || 'An error occurred during the call');
          setStatus('Error');
        },
      });
      
      console.log('[VoiceCall] Session created successfully');
      
      // Check if we should still keep this conversation (modal might have closed during init)
      if (!isOpen) {
        console.log('[VoiceCall] Modal closed during init, ending session immediately...');
        try {
          await conversation.endSession();
          console.log('[VoiceCall] Session ended successfully');
        } catch (e) {
          console.error('[VoiceCall] Error ending session:', e);
        }
        return;
      }
      
      // Store conversation
      conversationRef.current = conversation;
      
      // Store conversation ID
      try {
        const id = conversation.getId();
        if (id) {
          conversationIdRef.current = id;
          console.log('[VoiceCall] Conversation ID:', id);
        }
      } catch (err) {
        console.log('[VoiceCall] Conversation ID not yet available');
      }
      
    } catch (err: any) {
      console.error('[VoiceCall] Failed to initialize:', err);
      setError(err.message || 'Failed to start call. Please check your microphone permissions.');
      setStatus('Failed');
    } finally {
      isInitializingRef.current = false;
    }
  };
  
  const cleanupConversation = async () => {
    // Prevent multiple simultaneous cleanups
    if (isCleaningUpRef.current) {
      console.log('[VoiceCall] Already cleaning up, skipping');
      return;
    }
    
    // Check if there's anything to cleanup
    if (!conversationRef.current) {
      console.log('[VoiceCall] No conversation to cleanup');
      return;
    }
    
    isCleaningUpRef.current = true;
    const conversation = conversationRef.current;
    const convId = conversationIdRef.current;
    
    // Clear refs immediately to prevent reuse
    conversationRef.current = null;
    conversationIdRef.current = null;
    hasInitializedRef.current = false;
    
    console.log('[VoiceCall] Starting cleanup...');
    
    try {
      console.log('[VoiceCall] Calling endSession...');
      await conversation.endSession();
      console.log('[VoiceCall] Session ended successfully');
      
      // Mark consultation as complete in backend if we have a conversation ID
      if (convId && consultationId) {
        try {
          await fetch(`http://localhost:8000/api/voice/consultation/${consultationId}/complete?conversation_id=${convId}`, {
            method: 'POST',
          });
          console.log('[VoiceCall] Marked consultation complete');
        } catch (fetchErr) {
          console.error('[VoiceCall] Error marking complete:', fetchErr);
        }
      }
    } catch (err) {
      console.error('[VoiceCall] Error during cleanup:', err);
    } finally {
      isCleaningUpRef.current = false;
      
      // Reset all state
      setIsCallActive(false);
      setIsConnected(false);
      setError(null);
      setIsMuted(false);
      setStatus('Initializing...');
    }
  };

  const handleEndCall = async () => {
    console.log('[VoiceCall] handleEndCall called');
    
    // Call onClose() which will trigger useEffect cleanup via isOpen=false
    onClose();
  };

  const toggleMute = () => {
    if (conversationRef.current) {
      const newMutedState = !isMuted;
      conversationRef.current.setMicMuted(newMutedState);
      setIsMuted(newMutedState);
    }
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-80"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          handleEndCall();
        }
      }}
    >
      <div 
        className="bg-gray-900 rounded-2xl max-w-2xl w-full border border-gray-700 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="relative p-6 border-b border-gray-700">
          <button
            onClick={handleEndCall}
            className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
            aria-label="End Call"
          >
            <X size={24} />
          </button>
          
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Phone size={28} className="text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">{personaName}</h2>
              <p className="text-gray-400">Voice Consultation</p>
            </div>
          </div>
        </div>

        {/* Status */}
        <div className="p-6">
          <div className="flex items-center justify-center mb-6">
            {isConnected ? (
              <div className="flex items-center gap-2 text-green-400">
                <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                <span className="font-medium">{status}</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-yellow-400">
                <div className="w-3 h-3 bg-yellow-400 rounded-full animate-pulse"></div>
                <span className="font-medium">{status}</span>
              </div>
            )}
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 bg-red-900 bg-opacity-30 border border-red-500 rounded-lg">
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          )}

          {/* Call Instructions */}
          <div className="mb-8 text-center">
            <p className="text-gray-300 text-lg mb-2">Speak naturally with the expert</p>
            <p className="text-gray-500 text-sm">They will provide insights on your startup idea</p>
          </div>

          {/* Call Controls */}
          <div className="flex justify-center gap-4">
            <button
              onClick={toggleMute}
              disabled={!isCallActive}
              className={`p-4 rounded-full transition-colors ${
                isMuted
                  ? 'bg-red-600 hover:bg-red-700'
                  : 'bg-gray-700 hover:bg-gray-600'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
              aria-label={isMuted ? 'Unmute' : 'Mute'}
            >
              {isMuted ? <MicOff size={24} className="text-white" /> : <Mic size={24} className="text-white" />}
            </button>
            
            <button
              onClick={handleEndCall}
              className="p-4 rounded-full bg-red-600 hover:bg-red-700 transition-colors"
              aria-label="End Call"
            >
              <PhoneOff size={24} className="text-white" />
            </button>
          </div>

          {/* Instructions */}
          <p className="text-center text-gray-400 text-sm mt-4">
            {isCallActive 
              ? 'Speak naturally with the expert. They will provide insights on your startup idea.'
              : 'Please wait while we connect you...'}
          </p>
        </div>
      </div>
    </div>
  );
}

