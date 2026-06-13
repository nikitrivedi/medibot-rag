"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import ChatMessageBubble, { TypingIndicator } from "@/components/ChatMessage";
import Sidebar from "@/components/Sidebar";
import { chat } from "@/lib/api";
import {
  clearSession,
  getAccessibleCollections,
  getRoleLabel,
  hasSqlAccess,
  loadSession,
} from "@/lib/auth";
import type { ChatMessage, Session } from "@/lib/types";

const STARTER_PROMPTS = [
  "How many claims are pending?",
  "What is the cashless pre-auth SLA?",
  "What is the outbreak management protocol?",
];

export default function ChatPage() {
  const [session, setSession] = useState<Session | null>(null);
  const [authReady, setAuthReady] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const stored = loadSession();
    if (!stored) {
      window.location.href = "/login";
      return;
    }
    setSession(stored);
    setAuthReady(true);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function handleLogout() {
    clearSession();
    window.location.href = "/login";
  }

  async function sendMessage(text: string) {
    if (!session || !text.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setError("");
    setLoading(true);

    try {
      const response = await chat(text.trim(), session);
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.answer,
          retrieval_type: response.retrieval_type,
          sources: response.sources,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    sendMessage(question);
  }

  if (!authReady || !session) {
    return (
      <main className="flex min-h-screen items-center justify-center text-[var(--muted)]">
        Loading your session...
      </main>
    );
  }

  const collections = getAccessibleCollections(session.role);

  return (
    <div className="flex min-h-screen bg-[var(--bg)]">
      <Sidebar session={session} onLogout={handleLogout} />

      <div className="flex min-h-screen flex-1 flex-col">
        <header className="sticky top-0 z-10 border-b border-[var(--border)] bg-white/80 px-8 py-5 backdrop-blur-md">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold">Hospital Assistant</h2>
              <p className="mt-1 text-sm text-[var(--muted)]">
                {getRoleLabel(session.role)} · {collections.join(", ")} collections
                {hasSqlAccess(session.role) ? " · SQL analytics" : ""}
              </p>
            </div>
            <div className="hidden rounded-full border border-[var(--border)] bg-[var(--surface-muted)] px-4 py-2 text-sm text-slate-600 md:block">
              Secure role-scoped session
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto px-6 py-8 md:px-10">
          {messages.length === 0 ? (
            <div className="mx-auto max-w-3xl">
              <div className="rounded-[2rem] border border-[var(--border)] bg-white p-10 shadow-sm">
                <p className="text-sm font-medium uppercase tracking-[0.18em] text-[var(--primary)]">
                  Ready when you are
                </p>
                <h3 className="mt-3 text-3xl font-semibold leading-tight">
                  Ask about protocols, policies, equipment, or claims data
                </h3>
                <p className="mt-4 max-w-2xl text-base leading-7 text-[var(--muted)]">
                  MediBot routes document questions through hybrid RAG and analytical
                  questions through SQL RAG when your role allows it. Every answer
                  includes citations and a retrieval type label.
                </p>
                <div className="mt-8 flex flex-wrap gap-3">
                  {STARTER_PROMPTS.map((prompt) => (
                    <button
                      key={prompt}
                      type="button"
                      onClick={() => sendMessage(prompt)}
                      className="rounded-full border border-[var(--border)] bg-[var(--surface-muted)] px-4 py-2 text-sm transition hover:border-[var(--primary)] hover:bg-white"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="mx-auto flex max-w-4xl flex-col gap-6">
              {messages.map((message) => (
                <ChatMessageBubble key={message.id} message={message} />
              ))}
              {loading && <TypingIndicator />}
              <div ref={bottomRef} />
            </div>
          )}
        </div>

        <form
          onSubmit={handleSubmit}
          className="border-t border-[var(--border)] bg-white/90 px-6 py-5 backdrop-blur-md md:px-10"
        >
          {error && (
            <div className="mx-auto mb-3 max-w-4xl rounded-xl border border-red-100 bg-[var(--danger-soft)] px-4 py-3 text-sm text-[var(--danger)]">
              {error}
            </div>
          )}
          <div className="mx-auto flex max-w-4xl items-end gap-3">
            <div className="flex-1 rounded-[1.5rem] border border-[var(--border)] bg-[var(--surface-muted)] px-4 py-3 shadow-sm focus-within:border-[var(--primary)] focus-within:bg-white">
              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask about claims, procedures, equipment, policies..."
                className="w-full bg-transparent px-1 py-2 outline-none"
                disabled={loading}
              />
            </div>
            <button
              type="submit"
              disabled={loading || !question.trim()}
              className="rounded-2xl bg-[var(--primary)] px-6 py-3 font-medium text-white transition hover:bg-[var(--primary-hover)] disabled:opacity-60"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
