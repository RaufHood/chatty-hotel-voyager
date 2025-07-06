import { useState, useRef, useCallback, useEffect } from 'react';
import { apiService } from '@/services/api';

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
  
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const progressIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const speak = useCallback(async (text: string) => {
    try {
      setError(null);
      setIsProcessing(true);
      
      // Stop any current audio
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }

      // Get audio from backend TTS
      const audioBlob = await apiService.textToSpeech(text);
      const audioUrl = URL.createObjectURL(audioBlob);

      // Create audio element
      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      // Set up event handlers
      audio.onloadstart = () => {
        setIsProcessing(true);
      };

      audio.oncanplaythrough = () => {
        setIsProcessing(false);
        setIsPlaying(true);
        setProgress(0);
        
        // Start progress tracking
        progressIntervalRef.current = setInterval(() => {
          if (audio.duration) {
            const currentProgress = (audio.currentTime / audio.duration) * 100;
            setProgress(currentProgress);
          }
        }, 100);
      };

      audio.onended = () => {
        setIsPlaying(false);
        setProgress(100);
        if (progressIntervalRef.current) {
          clearInterval(progressIntervalRef.current);
        }
        setTimeout(() => setProgress(0), 1000);
        
        // Clean up
        URL.revokeObjectURL(audioUrl);
      };

      audio.onerror = (event) => {
        setIsPlaying(false);
        setIsProcessing(false);
        setProgress(0);
        setError('Failed to play audio. Please try again.');
        console.error('Audio playback error:', event);
        if (progressIntervalRef.current) {
          clearInterval(progressIntervalRef.current);
        }
        
        // Clean up
        URL.revokeObjectURL(audioUrl);
      };

      audio.onpause = () => {
        setIsPlaying(false);
        if (progressIntervalRef.current) {
          clearInterval(progressIntervalRef.current);
        }
      };

      audio.onplay = () => {
        setIsPlaying(true);
        // Resume progress tracking
        progressIntervalRef.current = setInterval(() => {
          if (audio.duration) {
            const currentProgress = (audio.currentTime / audio.duration) * 100;
            setProgress(currentProgress);
          }
        }, 100);
      };

      // Start playing
      await audio.play();
      
    } catch (err) {
      setIsProcessing(false);
      setIsPlaying(false);
      setError('Failed to convert text to speech. Please try again.');
      console.error('TTS error:', err);
    }
  }, []);

  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setIsPlaying(false);
    setIsProcessing(false);
    setProgress(0);
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current);
    }
  }, []);

  const pause = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
    }
  }, []);

  const resume = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.play();
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
      }
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