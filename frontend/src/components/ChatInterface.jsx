import { useState, useRef, useEffect } from 'react';
import { ragAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [attachedFile, setAttachedFile] = useState(null);

  const { user } = useAuth();
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load conversation history on component mount
  useEffect(() => {
    const loadConversations = async () => {
      try {
        const response = await ragAPI.getConversations();
        const conversations = response.data.conversations || [];

        // Don't load old conversations - start with a clean slate
        // This prevents confusion from seeing mixed conversations from different documents
        // New conversations will be added as the user chats
        setMessages([]);
      } catch (error) {
        console.error('Failed to load conversations:', error);
      }
    };

    loadConversations();
  }, []);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setAttachedFile(file);
    }
  };

  const handleRemoveFile = () => {
    setAttachedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleClearHistory = async () => {
    if (!window.confirm('Are you sure you want to clear all chat history? This action cannot be undone.')) {
      return;
    }

    try {
      await ragAPI.clearConversations();
      setMessages([]);
    } catch (error) {
      console.error('Failed to clear chat history:', error);
      alert('Failed to clear chat history. Please try again.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!query.trim()) return;

    const userMessage = {
      type: 'user',
      content: query,
      attachedFile: attachedFile?.name
    };
    setMessages((prev) => [...prev, userMessage]);

    const currentQuery = query;
    const currentFile = attachedFile;

    setQuery('');
    setAttachedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    setLoading(true);

    try {
      if (currentFile) {
        // Use upload-and-query endpoint when file is attached (non-streaming)
        const response = await ragAPI.uploadAndQuery(user.email, currentFile, currentQuery);
        const { answer, sources, document_used } = response.data;

        const aiMessage = {
          type: 'ai',
          content: answer,
          sources: sources || [],
          documentUsed: document_used,
        };

        setMessages((prev) => [...prev, aiMessage]);
        setLoading(false);
      } else {
        // Use streaming endpoint for regular queries
        // Add placeholder message for streaming
        const streamingMessageIndex = messages.length + 1;
        const aiMessage = {
          type: 'ai',
          content: '',
          sources: [],
          documentUsed: null,
          streaming: true,
        };
        setMessages((prev) => [...prev, aiMessage]);
        setLoading(false);

        await ragAPI.queryStream(
          user.email,
          currentQuery,
          // onChunk
          (chunk) => {
            setMessages((prev) => {
              const newMessages = [...prev];
              if (newMessages[streamingMessageIndex]) {
                newMessages[streamingMessageIndex] = {
                  ...newMessages[streamingMessageIndex],
                  content: newMessages[streamingMessageIndex].content + chunk,
                };
              }
              return newMessages;
            });
          },
          // onDone
          () => {
            setMessages((prev) => {
              const newMessages = [...prev];
              if (newMessages[streamingMessageIndex]) {
                newMessages[streamingMessageIndex] = {
                  ...newMessages[streamingMessageIndex],
                  streaming: false,
                };
              }
              return newMessages;
            });
          },
          // onError
          (error) => {
            const errorMessage = {
              type: 'error',
              content: `Streaming error: ${error}`,
            };
            setMessages((prev) => [...prev.slice(0, streamingMessageIndex), errorMessage]);
          }
        );
      }
    } catch (error) {
      const errorMessage = {
        type: 'error',
        content: error.response?.data?.error || error.response?.data?.detail || 'Failed to get response. Please try again.',
      };
      setMessages((prev) => [...prev, errorMessage]);
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 flex flex-col h-[600px]">
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-4 rounded-t-xl">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-xl font-semibold text-white">AI Chat</h2>
            <p className="text-blue-100 text-sm">Ask questions about your documents</p>
          </div>
          {messages.length > 0 && (
            <button
              onClick={handleClearHistory}
              className="px-3 py-2 bg-white bg-opacity-20 hover:bg-opacity-30 text-white rounded-lg text-sm font-medium transition flex items-center gap-2"
              title="Clear chat history"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
              Clear
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <svg
              className="w-16 h-16 mx-auto mb-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <p className="text-lg font-medium">Start a conversation</p>
            <p className="text-sm mt-2">Ask anything about your uploaded documents</p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-4 ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : message.type === 'error'
                  ? 'bg-red-50 border border-red-200 text-red-700'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {message.attachedFile && (
                <div className="mb-2 pb-2 border-b border-blue-400">
                  <span className="text-sm opacity-90">📎 {message.attachedFile}</span>
                </div>
              )}
              <p className="whitespace-pre-wrap">
                {message.content}
                {message.streaming && (
                  <span className="inline-block w-2 h-4 ml-1 bg-gray-800 animate-pulse"></span>
                )}
              </p>
              {message.documentUsed && (
                <div className="mt-2 pt-2 border-t border-gray-300">
                  <p className="text-xs opacity-75">📄 Context: {message.documentUsed}</p>
                </div>
              )}
              {message.sources && message.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-300">
                  <p className="text-sm font-semibold mb-2">Sources:</p>
                  <ul className="text-sm space-y-1">
                    {[...new Set(message.sources.map(s => s.metadata?.filename).filter(Boolean))].map((filename, idx) => (
                      <li key={idx} className="text-gray-600">
                        • {filename}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-4">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
        {attachedFile && (
          <div className="mb-2 flex items-center justify-between bg-blue-50 border border-blue-200 rounded-lg px-3 py-2">
            <span className="text-sm text-blue-700">📎 {attachedFile.name}</span>
            <button
              type="button"
              onClick={handleRemoveFile}
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              ✕
            </button>
          </div>
        )}
        <div className="flex space-x-2">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            accept=".pdf,.docx,.doc,.txt,.md"
            className="hidden"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition"
            disabled={loading}
            title="Attach a document"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M12 4v16m8-8H4"
              />
            </svg>
          </button>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatInterface;
