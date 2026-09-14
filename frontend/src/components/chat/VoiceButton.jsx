import React from 'react';
import { Mic, MicOff, Volume2 } from 'lucide-react';
import { useVoice } from '../../hooks/useVoice';

export function VoiceButton({ onTranscript, textToSpeak }) {
  const { isListening, isSpeaking, supported, toggleListening, speak } = useVoice({ onTranscript });

  if (!supported) return null;

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
      <button
        type="button"
        onClick={toggleListening}
        title={isListening ? 'Stop listening' : 'Start voice input'}
        style={{
          width: '34px',
          height: '34px',
          borderRadius: '50%',
          backgroundColor: isListening ? 'var(--crimson)' : 'var(--sand-200)',
          color: isListening ? '#FFFFFF' : 'var(--forest-800)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: isListening ? '0 0 12px rgba(201, 59, 59, 0.6)' : 'none',
          animation: isListening ? 'pulse-ring 1.5s infinite' : 'none',
        }}
      >
        {isListening ? <MicOff size={16} /> : <Mic size={16} />}
      </button>

      {textToSpeak && (
        <button
          type="button"
          onClick={() => speak(textToSpeak)}
          title="Read response aloud"
          style={{
            width: '34px',
            height: '34px',
            borderRadius: '50%',
            backgroundColor: isSpeaking ? 'var(--emerald)' : 'var(--sand-200)',
            color: isSpeaking ? '#FFFFFF' : 'var(--forest-800)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Volume2 size={16} />
        </button>
      )}
    </div>
  );
}
