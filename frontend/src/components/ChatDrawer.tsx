import React, { useState, useEffect, useRef } from 'react';
import { 
  X, 
  Send, 
  Sparkles, 
  Loader2, 
  BookOpen, 
  Trash2, 
  Bot, 
  User, 
  ArrowRight,
  HelpCircle
} from 'lucide-react';
import { budgetApi } from '../services/api';
import { ChatMessage } from '../types/budget';

interface ChatDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  workspaceId: string | null;
  budgetName?: string;
}

export const ChatDrawer: React.FC<ChatDrawerProps> = ({
  isOpen,
  onClose,
  workspaceId,
  budgetName,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([
    "Why has capital expenditure increased?",
    "Which sector received the highest allocation?",
    "What is the difference between budget estimates and revised estimates?",
    "How does this budget affect farmers and rural economy?",
    "What is the fiscal deficit and how is it financed?",
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load chat history when opened
  useEffect(() => {
    if (isOpen && workspaceId) {
      loadHistory();
    }
  }, [isOpen, workspaceId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const loadHistory = async () => {
    if (!workspaceId) return;
    try {
      const history = await budgetApi.getChatHistory(workspaceId);
      setMessages(history);
    } catch (e) {
      console.error('Failed to load chat history:', e);
    }
  };

  const handleSend = async (textToSend?: string) => {
    const query = (textToSend || input).trim();
    if (!query || !workspaceId || isLoading) return;

    setInput('');
    const tempUserMsg: ChatMessage = {
      id: String(Date.now()),
      role: 'user',
      content: query,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMsg]);
    setIsLoading(true);

    try {
      const res = await budgetApi.askQuestion(workspaceId, query);
      const assistantMsg: ChatMessage = {
        id: String(Date.now() + 1),
        role: 'assistant',
        content: res.message,
        sources: res.sources,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
      if (res.suggested_questions && res.suggested_questions.length > 0) {
        setSuggestions(res.suggested_questions);
      }
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: String(Date.now() + 1),
        role: 'assistant',
        content: `Error: ${err.message || 'Failed to process question. Please try again.'}`,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearHistory = async () => {
    if (!workspaceId) return;
    try {
      await budgetApi.clearChatHistory(workspaceId);
      setMessages([]);
    } catch (e) {
      console.error('Failed to clear history:', e);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[480px] bg-slate-900 border-l border-slate-800 shadow-2xl flex flex-col backdrop-blur-xl">
      
      {/* Header */}
      <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/90">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-1.5">
              AI Budget Copilot
              <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300">
                RAG Grounded
              </span>
            </h3>
            <p className="text-[11px] text-slate-400 truncate max-w-[260px]">
              {budgetName || 'Budget Q&A Engine'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {messages.length > 0 && (
            <button
              onClick={handleClearHistory}
              title="Clear conversation"
              className="p-1.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-slate-800 transition-colors"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          )}
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="space-y-4 pt-6">
            <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-800 text-center">
              <Bot className="h-8 w-8 text-indigo-400 mx-auto mb-2" />
              <h4 className="text-sm font-bold text-white">Ask Anything About This Budget</h4>
              <p className="text-xs text-slate-400 mt-1">
                Answers are synthesized directly from your uploaded official documents with exact numbers, formulas, and page citations.
              </p>
            </div>

            <div>
              <span className="text-xs font-semibold text-slate-400 block mb-2 px-1">
                Suggested Questions:
              </span>
              <div className="space-y-1.5">
                {suggestions.map((s, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(s)}
                    className="w-full text-left p-2.5 rounded-lg bg-slate-800/70 hover:bg-slate-800 border border-slate-700/60 hover:border-slate-600 text-xs text-slate-200 transition-all flex items-center justify-between group"
                  >
                    <span>{s}</span>
                    <ArrowRight className="h-3 w-3 text-slate-500 group-hover:text-indigo-400 shrink-0" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((msg) => {
          const isUser = msg.role === 'user';
          return (
            <div key={msg.id} className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
              {!isUser && (
                <div className="h-7 w-7 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center shrink-0 mt-0.5">
                  <Bot className="h-4 w-4" />
                </div>
              )}

              <div
                className={`max-w-[85%] rounded-2xl p-3.5 text-xs sm:text-sm leading-relaxed ${
                  isUser
                    ? 'bg-blue-600 text-white rounded-br-sm'
                    : 'bg-slate-800/90 text-slate-200 border border-slate-700/80 rounded-bl-sm space-y-2'
                }`}
              >
                <div className="whitespace-pre-wrap">{msg.content}</div>

                {/* Sources & Citations */}
                {!isUser && msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-slate-700/60 space-y-1.5">
                    <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1">
                      <BookOpen className="h-3 w-3 text-blue-400" />
                      Document Grounding & Page Citations
                    </div>
                    {msg.sources.map((src, i) => (
                      <div
                        key={i}
                        className="text-[11px] p-2 rounded bg-slate-900/60 border border-slate-800 text-slate-300"
                      >
                        <div className="font-semibold text-blue-300 mb-0.5">
                          {src.source || 'Document'} {src.page ? `(Page ${src.page})` : ''}
                        </div>
                        <div className="italic text-slate-400">"{src.text}"</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {isUser && (
                <div className="h-7 w-7 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center shrink-0 mt-0.5">
                  <User className="h-4 w-4" />
                </div>
              )}
            </div>
          );
        })}

        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="h-7 w-7 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center shrink-0">
              <Bot className="h-4 w-4" />
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-800/90 border border-slate-700 text-xs text-slate-300 flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin text-indigo-400" />
              <span>Synthesizing verified budget answer...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-3.5 border-t border-slate-800 bg-slate-900/90">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading || !workspaceId}
            placeholder={workspaceId ? "Ask any budget question..." : "Select a budget first"}
            className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading || !workspaceId}
            className="p-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white shadow-md shadow-indigo-600/30 transition-all shrink-0"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>

    </div>
  );
};

