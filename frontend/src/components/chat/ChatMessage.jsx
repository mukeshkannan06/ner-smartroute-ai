import React from 'react';
import { Bot, User, Volume2 } from 'lucide-react';
import { useVoice } from '../../hooks/useVoice';

export function ChatMessage({ message, onSuggestionClick }) {
  const isBot = message.sender === 'bot';
  const { speak } = useVoice();

  return (
    <div style={{
      display: 'flex',
      gap: '10px',
      marginBottom: '16px',
      flexDirection: isBot ? 'row' : 'row-reverse',
    }}>
      {/* Avatar */}
      <div style={{
        width: '30px',
        height: '30px',
        borderRadius: '8px',
        backgroundColor: isBot ? 'var(--forest-800)' : 'var(--clay-600)',
        color: '#FFFFFF',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        fontSize: '12px',
      }}>
        {isBot ? <Bot size={16} /> : <User size={16} />}
      </div>

      {/* Content Bubble */}
      <div style={{
        maxWidth: '82%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: isBot ? 'flex-start' : 'flex-end',
      }}>
        <div style={{
          padding: '12px 16px',
          borderRadius: 'var(--radius-md)',
          backgroundColor: isBot ? '#FFFFFF' : 'var(--forest-800)',
          color: isBot ? 'var(--text-main)' : '#FFFFFF',
          border: isBot ? '1px solid var(--border-color)' : 'none',
          boxShadow: 'var(--shadow-sm)',
          fontSize: '13px',
          whiteSpace: 'pre-wrap',
          lineHeight: '1.45',
          position: 'relative',
        }}>
          {message.text}

          {isBot && message.text && (
            <button
              onClick={() => speak(message.text)}
              title="Speak"
              style={{
                position: 'absolute',
                top: '8px',
                right: '8px',
                padding: '2px',
                color: 'var(--text-light)',
                borderRadius: '4px',
              }}
            >
              <Volume2 size={13} />
            </button>
          )}
        </div>

        {/* Suggestions chips */}
        {isBot && message.suggestions && message.suggestions.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '8px' }}>
            {message.suggestions.map((sug, idx) => (
              <button
                key={idx}
                onClick={() => onSuggestionClick(sug)}
                style={{
                  padding: '4px 10px',
                  borderRadius: 'var(--radius-full)',
                  backgroundColor: 'var(--sand-200)',
                  color: 'var(--forest-900)',
                  fontSize: '11.5px',
                  fontWeight: 500,
                  border: '1px solid var(--border-color)',
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--sand-400)'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'var(--sand-200)'}
              >
                {sug}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
