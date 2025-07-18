
import React, { useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Volume2, VolumeX, Loader2, Pause, Play, Mic } from 'lucide-react';
import { useTextToSpeech } from '@/hooks/use-text-to-speech';

interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
  autoPlayTTS?: boolean;
  isVoiceMessage?: boolean;
}

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage = ({ message }: ChatMessageProps) => {
  const { 
    isPlaying, 
    isProcessing, 
    progress, 
    speak, 
    stop, 
    pause, 
    resume,
    error: ttsError 
  } = useTextToSpeech();
  
  const hasAutoPlayed = useRef(false);

  const handleTTSToggle = () => {
    if (isPlaying) {
      pause();
    } else if (isProcessing) {
      stop();
    } else {
      speak(message.content);
    }
  };

  const handleTTSStop = () => {
    stop();
  };

  // Auto-play TTS for voice-initiated messages (only once)
  useEffect(() => {
    if (message.autoPlayTTS && message.role === "assistant" && !hasAutoPlayed.current) {
      hasAutoPlayed.current = true;
      // Add a small delay to ensure the message is fully rendered
      const timer = setTimeout(() => {
        speak(message.content);
      }, 500);
      
      return () => clearTimeout(timer);
    }
  }, [message.autoPlayTTS, message.content, message.role]);

  return (
    <div
      className={`chat-bubble ${
        message.role === "user" ? "chat-bubble-user" : "chat-bubble-assistant"
      }`}
    >
      <p className="text-sm leading-relaxed">{message.content}</p>
      
      <div className="flex items-center justify-between mt-2">
        <div className="flex items-center gap-2">
          <p className="text-xs opacity-70">
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
          {message.isVoiceMessage && (
            <div className="flex items-center gap-1">
              <Mic className="w-3 h-3 text-blue-500" />
              <span className="text-xs text-blue-500">Voice</span>
            </div>
          )}
        </div>
        
        {/* TTS Controls for assistant messages */}
        {message.role === "assistant" && (
          <div className="flex items-center gap-1">
            {isProcessing && (
              <div className="flex items-center gap-1 text-xs text-blue-600">
                <Loader2 className="w-3 h-3 animate-spin" />
                <span>{message.autoPlayTTS ? 'Auto-playing...' : 'Processing...'}</span>
              </div>
            )}
            
            {isPlaying && (
              <div className="flex items-center gap-1">
                {message.autoPlayTTS && (
                  <span className="text-xs text-green-600 mr-1">Auto</span>
                )}
                <div className="w-12 h-1 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-500 transition-all duration-100"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleTTSStop}
                  className="h-6 w-6 p-0 opacity-70 hover:opacity-100"
                >
                  <VolumeX className="w-3 h-3" />
                </Button>
              </div>
            )}
            
            {!isProcessing && !isPlaying && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleTTSToggle}
                className="h-6 w-6 p-0 opacity-70 hover:opacity-100"
              >
                <Volume2 className="w-3 h-3" />
              </Button>
            )}
          </div>
        )}
      </div>
      
      {ttsError && (
        <p className="text-xs text-red-500 mt-1">{ttsError}</p>
      )}
    </div>
  );
};
