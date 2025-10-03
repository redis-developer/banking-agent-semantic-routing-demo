'use client';

import { useState } from 'react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
}

export default function ChatDock() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  const handleSend = async () => {
    if (!inputText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      sender: 'user'
    };

    // Add user message to the list
    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputText;
    setInputText('');
    setIsLoading(true);

    try {
      // Call POST /chat on FastAPI backend
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: currentInput }),
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: data.reply || 'Sorry, I could not process your request.',
          sender: 'assistant'
        };

        // Add assistant reply to the list
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        // Handle error case
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: 'Sorry, there was an error processing your request.',
          sender: 'assistant'
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      // Handle network error
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, there was a network error.',
        sender: 'assistant'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isLoading) {
      handleSend();
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Chat Window */}
      {isOpen && (
        <div className="mb-4 w-96 h-[32rem] backdrop-blur-lg bg-glass-light rounded-2xl shadow-glass-lg border border-glass-medium overflow-hidden animate-in slide-in-from-bottom-2 fade-in duration-300">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-glass-medium bg-glass-dark/50">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-accent-neon rounded-full animate-pulse"></div>
              <h3 className="text-white font-semibold">AI Assistant</h3>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white/60 hover:text-white transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Messages List */}
          <div className="flex-1 p-4 space-y-3 overflow-y-auto h-80 scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
            {messages.length === 0 ? (
              <div className="text-white/60 text-center py-8 text-sm">
                💬 Hello! I'm your AI banking assistant. How can I help you today?
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs px-3 py-2 rounded-xl text-sm font-medium ${
                      message.sender === 'user'
                        ? 'bg-gradient-accent text-dark-950 shadow-neon'
                        : 'bg-glass-medium backdrop-blur-sm text-white border border-glass-light'
                    }`}
                  >
                    {message.text}
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-glass-medium backdrop-blur-sm text-white/80 px-3 py-2 rounded-xl border border-glass-light animate-pulse">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-1.5 h-1.5 bg-accent-neon rounded-full animate-bounce"></div>
                      <div className="w-1.5 h-1.5 bg-accent-neon rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-1.5 h-1.5 bg-accent-neon rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                    <span className="text-xs">AI is typing...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input Section */}
          <div className="border-t border-glass-medium bg-glass-dark/50 backdrop-blur-sm p-4">
            <div className="flex space-x-2">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                disabled={isLoading}
                className="flex-1 px-3 py-2 bg-glass-medium backdrop-blur-sm border border-glass-light rounded-lg text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-accent-neon focus:border-accent-neon disabled:opacity-50 transition-all duration-200 text-sm"
              />
              <button
                onClick={handleSend}
                disabled={isLoading || !inputText.trim()}
                className="px-4 py-2 bg-gradient-accent text-dark-950 rounded-lg hover:shadow-neon focus:outline-none focus:ring-2 focus:ring-accent-neon disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-semibold"
              >
                {isLoading ? (
                  <div className="w-4 h-4 border-2 border-dark-950/30 border-t-dark-950 rounded-full animate-spin"></div>
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Floating Chat Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`w-14 h-14 rounded-full shadow-glass-lg backdrop-blur-lg border border-glass-medium transition-all duration-300 flex items-center justify-center group ${
          isOpen 
            ? 'bg-glass-medium hover:bg-glass-light' 
            : 'bg-gradient-accent hover:shadow-neon-lg transform hover:scale-110'
        }`}
      >
        {isOpen ? (
          <svg className="w-6 h-6 text-white transition-transform group-hover:rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <div className="relative">
            <svg className="w-6 h-6 text-dark-950 transition-transform group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            {messages.length > 0 && (
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></div>
            )}
          </div>
        )}
      </button>
    </div>
  );
}
