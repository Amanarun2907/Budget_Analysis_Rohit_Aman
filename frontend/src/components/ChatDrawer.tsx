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
  ChevronDown,
} from 'lucide-react';
import { budgetApi } from '../services/api';
import { ChatMessage } from '../types/budget';

interface ChatDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  workspaceId: string | null;
  budgetName?: string;
}

// ─────────────────────────── Markdown renderer ───────────────────────────────
// Lightweight inline renderer — no external library needed.
function renderMarkdown(text: string): React.ReactNode {
  const lines = text.split('\n');
  const elements: React.ReactNode[] = [];
  let key = 0;

  const inlineFormat = (line: string): React.ReactNode => {
    // Bold **text**
    const parts = line.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="text-white font-semibold">{part.slice(2, -2)}</strong>;
      }
      // Inline code `text`
      if (part.startsWith('`') && part.endsWith('`')) {
        return <code key={i} className="px-1 py-0.5 rounded bg-slate-800 text-blue-300 text-[11px] font-mono">{part.slice(1, -1)}</code>;
      }
      return part;
    });
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    if (!trimmed) {
      elements.push(<div key={key++} className="h-2" />);
      continue;
    }

    // ### Heading
    if (trimmed.startsWith('### ')) {
      elements.push(
        <h4 key={key++} className="text-sm font-bold text-white mt-3 mb-1">
          {trimmed.slice(4)}
        </h4>
      );
      continue;
    }

    // ## Heading
    if (trimmed.startsWith('## ')) {
      elements.push(
        <h3 key={key++} className="text-sm font-bold text-blue-300 mt-3 mb-1">
          {trimmed.slice(3)}
        </h3>
      );
      continue;
    }

    // Numbered list
    const numMatch = trimmed.match(/^(\d+)\.\s+(.+)/);
    if (numMatch) {
      elements.push(
        <div key={key++} className="flex gap-2 my-0.5">
          <span className="text-blue-400 font-semibold shrink-0 w-5 text-right">{numMatch[1]}.</span>
          <span className="text-slate-200">{inlineFormat(numMatch[2])}</span>
        </div>
      );
      continue;
    }

    // Bullet list (- or *)
    if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      elements.push(
        <div key={key++} className="flex gap-2 my-0.5 pl-1">
          <span className="text-blue-400 shrink-0 mt-1">•</span>
          <span className="text-slate-200">{inlineFormat(trimmed.slice(2))}</span>
        </div>
      );
      continue;
    }

    // Blockquote
    if (trimmed.startsWith('> ')) {
      elements.push(
        <blockquote key={key++} className="border-l-2 border-blue-500/50 pl-3 italic text-slate-400 my-1 text-xs">
          {inlineFormat(trimmed.slice(2))}
        </blockquote>
      );
      continue;
    }

    // Regular paragraph
    elements.push(
      <p key={key++} className="text-slate-200 leading-relaxed my-0.5">
        {inlineFormat(trimmed)}
      </p>
    );
  }

  return <>{elements}</>;
}

// ────────────────────────────────────────────────────────────────────────────

const STARTER_QUESTIONS = [
  'What is the total capital expenditure and how does it compare to last year?',
  'Which sector received the highest allocation and why?',
  'Explain the fiscal deficit and how it is being financed.',
  'What welfare schemes were allocated the most funds?',
  'What tax reforms were announced in this budget?',
];

export const ChatDrawer: React.FC<ChatDrawerProps> = ({
  isOpen,
  onClose,
  workspaceId,
  budgetName,
}) => {
  const [messages, setMessages]       = useState<ChatMessage[]>([]);
  const [input, setInput]             = useState('');
  const [isLoading, setIsLoading]     = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>(STARTER_QUESTIONS);
  const [sourcesOpen, setSourcesOpen] = useState<Record<string, boolean>>({});

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef        = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen && workspaceId) loadHistory();
  }, [isOpen, workspaceId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  useEffect(() => {
    if (isOpen) setTimeout(() => inputRef.current?.focus(), 150);
  }, [isOpen]);

  const loadHistory = async () => {
    if (!workspaceId) return;
    try {
      const history = await budgetApi.getChatHistory(workspaceId);
      setMessages(history);
    } catch (e) {
      console.error('Chat history load error:', e);
    }
  };

  const handleSend = async (textOverride?: string) => {
    const query = (textOverride ?? input).trim();
    if (!query || !workspaceId || isLoading) return;

    setInput('');
    const tempUser: ChatMessage = {
      id:         String(Date.now()),
      role:       'user',
      content:    query,
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, tempUser]);
    setIsLoading(true);

    try {
      const res = await budgetApi.askQuestion(workspaceId, query);
      const aiMsg: ChatMessage = {
        id:         String(Date.now() + 1),
        role:       'assistant',
        content:    res.message,
        sources:    res.sources,
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, aiMsg]);
      if (res.suggested_questions?.length) setSuggestions(res.suggested_questions);
    } catch (err: any) {
      setMessages(prev => [...prev, {
        id:         String(Date.now() + 1),
        role:       'assistant',
        content:    `**Error:** ${err.message || 'Could not process your question. Please try again.'}`,
        created_at: new Date().toISOString(),
      }]);
    } finally {
      setIsLoading(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleClear = async () => {
    if (!workspaceId) return;
    try {
      await budgetApi.clearChatHistory(workspaceId);
      setMessages([]);
      setSuggestions(STARTER_QUESTIONS);
    } catch (e) {
      console.error('Clear history error:', e);
    }
  };

  const toggleSources = (msgId: string) =>
    setSourcesOpen(prev => ({ ...prev, [msgId]: !prev[msgId] }));

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[500px] bg-slate-950 border-l border-slate-800 shadow-2xl flex flex-col">

      {/* ── Header ── */}
      <div className="px-5 py-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-950 shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-indigo-500/15 text-indigo-400">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              AI Budget Analyst
              <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/20">
                RAG · Groq
              </span>
            </h3>
            <p className="text-[11px] text-slate-400 truncate max-w-[260px]">
              {budgetName || 'Ask anything about this budget'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {messages.length > 0 && (
            <button
              onClick={handleClear}
              title="Clear conversation"
              className="p-1.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-slate-900 transition-colors"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          )}
          <button onClick={onClose} className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-900 transition-colors">
            <X className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* ── Messages ── */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">

        {/* Empty state with starter questions */}
        {messages.length === 0 && (
          <div className="space-y-4 pt-4">
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
              <Bot className="h-9 w-9 text-indigo-400 mx-auto mb-2" />
              <h4 className="text-sm font-bold text-white">Ask Anything About This Budget</h4>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                Answers are grounded in your uploaded official documents with exact ₹ Crore figures
                and page-level citations.
              </p>
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-400 px-1 mb-2">Suggested Questions</p>
              <div className="space-y-1.5">
                {suggestions.map((s, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(s)}
                    className="w-full text-left p-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-xs text-slate-200 transition-all flex items-center justify-between group"
                  >
                    <span className="leading-snug">{s}</span>
                    <ArrowRight className="h-3.5 w-3.5 text-slate-500 group-hover:text-indigo-400 shrink-0 ml-2" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Message bubbles */}
        {messages.map((msg) => {
          const isUser = msg.role === 'user';
          const hasSources = !isUser && msg.sources && msg.sources.length > 0;
          const srcOpen = sourcesOpen[msg.id];

          return (
            <div key={msg.id} className={`flex gap-2.5 ${isUser ? 'justify-end' : 'justify-start'}`}>

              {!isUser && (
                <div className="h-7 w-7 rounded-lg bg-indigo-500/15 text-indigo-400 flex items-center justify-center shrink-0 mt-0.5">
                  <Bot className="h-4 w-4" />
                </div>
              )}

              <div className={`max-w-[88%] flex flex-col gap-1.5 ${isUser ? 'items-end' : 'items-start'}`}>
                <div
                  className={`rounded-2xl px-4 py-3 text-xs leading-relaxed ${
                    isUser
                      ? 'bg-blue-600 text-white rounded-br-sm'
                      : 'bg-slate-900 border border-slate-800 text-slate-100 rounded-bl-sm'
                  }`}
                >
                  {isUser
                    ? <span>{msg.content}</span>
                    : <div className="space-y-1">{renderMarkdown(msg.content)}</div>
                  }
                </div>

                {/* Collapsible sources */}
                {hasSources && (
                  <div className="w-full">
                    <button
                      onClick={() => toggleSources(msg.id)}
                      className="flex items-center gap-1.5 text-[10px] text-slate-400 hover:text-blue-400 transition-colors px-1"
                    >
                      <BookOpen className="h-3 w-3" />
                      <span>{msg.sources!.length} document source{msg.sources!.length > 1 ? 's' : ''}</span>
                      <ChevronDown className={`h-3 w-3 transition-transform ${srcOpen ? 'rotate-180' : ''}`} />
                    </button>
                    {srcOpen && (
                      <div className="mt-1.5 space-y-1.5">
                        {msg.sources!.map((src, i) => (
                          <div
                            key={i}
                            className="text-[11px] p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-slate-300"
                          >
                            <div className="font-semibold text-blue-300 mb-0.5">
                              {src.source || 'Budget Document'}{src.page ? ` — Page ${src.page}` : ''}
                              {src.relevance && (
                                <span className="ml-2 text-slate-500 font-normal">
                                  relevance: {(src.relevance * 100).toFixed(0)}%
                                </span>
                              )}
                            </div>
                            <div className="italic text-slate-400 leading-snug">"{src.text}"</div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {isUser && (
                <div className="h-7 w-7 rounded-lg bg-blue-500/15 text-blue-400 flex items-center justify-center shrink-0 mt-0.5">
                  <User className="h-4 w-4" />
                </div>
              )}
            </div>
          );
        })}

        {/* Typing indicator */}
        {isLoading && (
          <div className="flex gap-2.5 justify-start">
            <div className="h-7 w-7 rounded-lg bg-indigo-500/15 text-indigo-400 flex items-center justify-center shrink-0">
              <Bot className="h-4 w-4" />
            </div>
            <div className="px-4 py-3 rounded-2xl rounded-bl-sm bg-slate-900 border border-slate-800 text-xs text-slate-300 flex items-center gap-2">
              <Loader2 className="h-3.5 w-3.5 animate-spin text-indigo-400" />
              <span>Analysing budget data…</span>
            </div>
          </div>
        )}

        {/* Suggested follow-ups after last AI message */}
        {messages.length > 0 && !isLoading && messages[messages.length - 1].role === 'assistant' && suggestions.length > 0 && (
          <div className="space-y-1">
            <p className="text-[10px] text-slate-500 px-1">Continue with:</p>
            {suggestions.slice(0, 2).map((s, i) => (
              <button
                key={i}
                onClick={() => handleSend(s)}
                className="w-full text-left px-3 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-[11px] text-slate-300 hover:text-white flex items-center justify-between gap-2 transition-all group"
              >
                <span>{s}</span>
                <ArrowRight className="h-3 w-3 shrink-0 text-slate-500 group-hover:text-indigo-400" />
              </button>
            ))}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* ── Input ── */}
      <div className="p-3.5 border-t border-slate-800 bg-slate-950 shrink-0">
        {!workspaceId && (
          <p className="text-xs text-amber-400 text-center mb-2">
            Please select or upload a budget to enable Q&amp;A.
          </p>
        )}
        <form
          onSubmit={e => { e.preventDefault(); handleSend(); }}
          className="flex items-center gap-2"
        >
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            disabled={isLoading || !workspaceId}
            placeholder={workspaceId ? 'Ask any budget question…' : 'Select a budget first'}
            className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:opacity-50 transition-all"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading || !workspaceId}
            className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed text-white shadow-lg shadow-indigo-600/20 transition-all shrink-0"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>

    </div>
  );
};
