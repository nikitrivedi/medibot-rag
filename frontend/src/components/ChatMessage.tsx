import SourceList from "@/components/SourceList";
import type { ChatMessage } from "@/lib/types";

function RetrievalBadge({ retrievalType }: { retrievalType?: string }) {
  if (!retrievalType) return null;

  const isSql = retrievalType.toLowerCase().includes("sql");
  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold tracking-wide ${
        isSql
          ? "bg-[var(--accent-soft)] text-[var(--accent)]"
          : "bg-[var(--primary-soft)] text-[var(--primary)]"
      }`}
    >
      {retrievalType}
    </span>
  );
}

export default function ChatMessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      <div
        className={`mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-semibold ${
          isUser
            ? "bg-[var(--primary)] text-white"
            : "border border-[var(--border)] bg-white text-[var(--primary)]"
        }`}
      >
        {isUser ? "You" : "AI"}
      </div>

      <div className={`max-w-3xl ${isUser ? "text-right" : "text-left"}`}>
        <div
          className={`rounded-3xl px-5 py-4 shadow-sm ${
            isUser
              ? "bg-[var(--primary)] text-white"
              : "border border-[var(--border)] bg-white text-[var(--text)]"
          }`}
        >
          {!isUser && (
            <div className="mb-3">
              <RetrievalBadge retrievalType={message.retrieval_type} />
            </div>
          )}
          <p className="whitespace-pre-wrap text-[15px] leading-7">{message.content}</p>
          {!isUser && message.sources && <SourceList sources={message.sources} />}
        </div>
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex gap-3">
      <div className="mt-1 flex h-9 w-9 items-center justify-center rounded-full border border-[var(--border)] bg-white text-sm font-semibold text-[var(--primary)]">
        AI
      </div>
      <div className="rounded-3xl border border-[var(--border)] bg-white px-5 py-4 shadow-sm">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-[var(--primary)] typing-dot" />
          <span className="h-2 w-2 rounded-full bg-[var(--primary)] typing-dot" />
          <span className="h-2 w-2 rounded-full bg-[var(--primary)] typing-dot" />
          <span className="ml-2 text-sm text-[var(--muted)]">MediBot is thinking</span>
        </div>
      </div>
    </div>
  );
}

export { TypingIndicator };
