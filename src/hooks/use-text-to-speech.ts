import { useState, useRef, useCallback, useEffect } from 'react';

interface UseTextToSpeechReturn {
  isPlaying: boolean;
  isProcessing: boolean;
  progress: number;
  speak: (text: string) => Promise<void>;
  stop: () => void;
  pause: () => void;
  resume: () => void;
  error: string | null;
}

export const useTextToSpeech = (): UseTextToSpeechReturn => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const progressIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const speak = useCallback(async (text: string) => {
    try {
      setError(null);
      setIsProcessing(true);
      
      // Stop any current speech
      if (utteranceRef.current) {
        speechSynthesis.cancel();
      }

      // Create new utterance
      const utterance = new SpeechSynthesisUtterance(text);
      utteranceRef.current = utterance;

      // Configure voice settings
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 1;

      // Try to use a more natural voice if available
      const voices = speechSynthesis.getVoices();
      const preferredVoice = voices.find(voice => 
        voice.lang.includes('en') && 
        (voice.name.includes('Neural') || voice.name.includes('Premium') || voice.name.includes('Enhanced'))
      ) || voices.find(voice => voice.lang.includes('en')) || voices[0];
      
      if (preferredVoice) {
        utterance.voice = preferredVoice;
      }

      // Set up event handlers
      utterance.onstart = () => {
        setIsProcessing(false);
        setIsPlaying(true);
        setProgress(0);
        
        // Start progress tracking
        progressIntervalRef.current = setInterval(() => {
          setProgress(prev => Math.min(prev + 2, 95)); // Approximate progress
        }, 100);
      };

      utterance.onend = () => {
        setIsPlaying(false);
        setProgress(100);
        if (progressIntervalRef.current) {
          clearInterval(progressIntervalRef.current);
        }
        setTimeout(() => setProgress(0), 1000);
      };

      utterance.onerror = (event) => {
        setIsPlaying(false);
        setIsProcessing(false);
        setProgress(0);
        setError('Failed to play audio. Please try again.');
        console.error('Speech synthesis error:', event);
        if (progressIntervalRef.current) {
          clearInterval(progressIntervalRef.current);
        }
      };

      utterance.onpause = () => {
        setIsPlaying(false);
        if (progressIntervalRef.current) {
          clearInterval(progressIntervalRef.current);
        }
      };

      utterance.onresume = () => {
        setIsPlaying(true);
        // Resume progress tracking
        progressIntervalRef.current = setInterval(() => {
          setProgress(prev => Math.min(prev + 2, 95));
        }, 100);
      };

      // Start speaking
      speechSynthesis.speak(utterance);
      
    } catch (err) {
      setIsProcessing(false);
      setIsPlaying(false);
      setError('Speech synthesis not supported in this browser.');
      console.error('TTS error:', err);
    }
  }, []);

  const stop = useCallback(() => {
    speechSynthesis.cancel();
    setIsPlaying(false);
    setIsProcessing(false);
    setProgress(0);
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current);
    }
  }, []);

  const pause = useCallback(() => {
    speechSynthesis.pause();
  }, []);

  const resume = useCallback(() => {
    speechSynthesis.resume();
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      speechSynthesis.cancel();
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
    };
  }, []);

  return {
    isPlaying,
    isProcessing,
    progress,
    speak,
    stop,
    pause,
    resume,
    error
  };
}; 