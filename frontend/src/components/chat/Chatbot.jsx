import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, Sparkles, X, Minimize2, Maximize2 } from 'lucide-react';
import { ChatMessage } from './ChatMessage';
import { VoiceButton } from './VoiceButton';
import { useLanguage } from '../../context/LanguageContext';
import { useRouteContext } from '../../context/RouteContext';
import { sendChatMessage } from '../../services/chatService';

export function Chatbot() {
  const { language, t } = useLanguage();
  const { setRouteResults, setTwinImpact, refreshNetwork, origin, destination } = useRouteContext();

  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: "Hello! I'm NER SmartRoute AI Assistant. Ask me to plan optimal routes, inspect weather or landslide risks, or simulate road closures across North-East India.",
      suggestions: [
        'Route Guwahati to Imphal',
        'Weather in Shillong',
        'Show active incidents',
        'Simulate road closure on NH-001',
      ],
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (messageText) => {
    const textToSend = messageText || input;
    if (!textToSend.trim()) return;

    const userMsg = { sender: 'user', text: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await sendChatMessage({
        message: textToSend,
        language,
        context: { origin, destination },
      });

      const botMsg = {
        sender: 'bot',
        text: res.reply,
        suggestions: res.suggestions || [],
        action: res.action,
        data: res.data,
      };

      setMessages((prev) => [...prev, botMsg]);

      // Handle map / UI synchronization actions
      if (res.action === 'SHOW_ROUTE' && res.data) {
        setRouteResults(res.data);
      } else if (res.action === 'SIMULATE_CLOSURE' && res.data) {
        setTwinImpact(res.data);
        refreshNetwork();
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: "I'm having trouble connecting to the backend. Please ensure the FastAPI server is running.",
          suggestions: ['Retry'],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleTranscript = (transcriptText) => {
    setInput(transcriptText);
    handleSend(transcriptText);
  };

  return (
    <>
      {/* Floating Toggle Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="chatbot-floating-toggle"
        >
          <Sparkles size={18} color="var(--clay-400)" />
          <span className="chatbot-toggle-text">AI Route Assistant</span>
        </button>
      )}

      {/* Floating Chat Modal */}
      {isOpen && (
        <div className="chatbot-modal">
          {/* Header */}
          <div style={{
            padding: '14px 18px',
            backgroundColor: 'var(--forest-900)',
            color: '#FFFFFF',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                width: '26px',
                height: '26px',
                borderRadius: '6px',
                backgroundColor: 'var(--clay-600)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}>
                <Sparkles size={15} color="#fff" />
              </div>
              <div>
                <h4 style={{ fontSize: '13.5px', color: '#FFFFFF' }}>{t('chat.title')}</h4>
                <div style={{ fontSize: '10px', color: 'var(--moss-light)' }}>Multilingual NLP & Voice</div>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              style={{ color: 'var(--sand-400)', padding: '4px' }}
            >
              <X size={18} />
            </button>
          </div>

          {/* Message List */}
          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: '16px',
            backgroundColor: 'var(--sand-50)',
          }}>
            {messages.map((m, idx) => (
              <ChatMessage
                key={idx}
                message={m}
                onSuggestionClick={(sug) => handleSend(sug)}
              />
            ))}
            {loading && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 12px',
                fontSize: '12px',
                color: 'var(--text-muted)',
              }}>
                <span className="animate-spin">⏳</span>
                <span>Thinking & calculating route graphs...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Footer */}
          <div style={{
            padding: '12px',
            backgroundColor: '#FFFFFF',
            borderTop: '1px solid var(--border-color)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}>
            <VoiceButton onTranscript={handleTranscript} />
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder={t('chat.placeholder')}
              style={{
                flex: 1,
                padding: '8px 12px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-color)',
                fontSize: '13px',
                outline: 'none',
              }}
            />
            <button
              onClick={() => handleSend()}
              disabled={loading || !input.trim()}
              style={{
                width: '34px',
                height: '34px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--forest-800)',
                color: '#FFFFFF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                opacity: input.trim() ? 1 : 0.5,
              }}
            >
              <Send size={15} />
            </button>
          </div>
        </div>
      )}
    </>
  );
}
