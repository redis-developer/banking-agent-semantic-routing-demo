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
      // Call POST /api/chat
      const response = await fetch('/api/chat', {
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
    <div className="flex flex-col h-96 max-w-2xl mx-auto border border-gray-300 rounded-lg">
      {/* Messages List */}
      <div className="flex-1 p-4 space-y-3 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="text-gray-500 text-center">No messages yet. Start a conversation!</div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs px-3 py-2 rounded-lg text-sm ${
                  message.sender === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-800'
                }`}
              >
                {message.text}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-200 text-gray-800 px-3 py-2 rounded-lg text-sm">
              Typing...
            </div>
          </div>
        )}
      </div>

      {/* Input Section */}
      <div className="border-t border-gray-300 p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={isLoading}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !inputText.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
