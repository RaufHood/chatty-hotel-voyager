
import React from 'react';
import { Button } from '@/components/ui/button';
import { Volume2, VolumeX, Loader2, Pause, Play } from 'lucide-react';
import { useTextToSpeech } from '@/hooks/use-text-to-speech';

interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
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

  return (
    <div
      className={`chat-bubble ${
        message.role === "user" ? "chat-bubble-user" : "chat-bubble-assistant"
      }`}
    >
      <p className="text-sm leading-relaxed">{message.content}</p>
      
      <div className="flex items-center justify-between mt-2">
        <p className="text-xs opacity-70">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
        
        {/* TTS Controls for assistant messages */}
        {message.role === "assistant" && (
          <div className="flex items-center gap-1">
            {isProcessing && (
              <div className="flex items-center gap-1 text-xs text-blue-600">
                <Loader2 className="w-3 h-3 animate-spin" />
                <span>Processing...</span>
              </div>
            )}
            
            {isPlaying && (
              <div className="flex items-center gap-1">
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
