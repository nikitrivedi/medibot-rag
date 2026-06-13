import type { Source } from "@/lib/types";

function formatSectionTitle(title: string | string[]): string {
  return Array.isArray(title) ? title.join(" › ") : title;
}

function DocumentSource({
  source,
  index,
}: {
  source: Extract<Source, { type: "document" }>;
  index: number;
}) {
  return (
    <details className="group rounded-2xl border border-[var(--border)] bg-[var(--surface-muted)]">
      <summary className="cursor-pointer list-none px-4 py-3 marker:content-none">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-sm font-medium text-slate-800">
              Source {index + 1}: {source.source_document.split("/").pop()}
            </p>
            <p className="mt-1 text-xs text-[var(--muted)]">
              {formatSectionTitle(source.section_title)} · {source.collection}
            </p>
          </div>
          <span className="rounded-full bg-white px-2 py-1 text-xs text-[var(--muted)]">
            {source.rerank_score.toFixed(2)}
          </span>
        </div>
      </summary>
      <div className="border-t border-[var(--border)] px-4 py-3 text-sm leading-6 text-slate-700">
        {source.text}
      </div>
    </details>
  );
}

function SqlSource({ source }: { source: Extract<Source, { type: "sql" }> }) {
  return (
    <details className="rounded-2xl border border-[var(--border)] bg-[var(--surface-muted)]" open>
      <summary className="cursor-pointer px-4 py-3 text-sm font-medium text-slate-800">
        SQL source
      </summary>
      <div className="space-y-3 border-t border-[var(--border)] px-4 py-3">
        <pre className="overflow-x-auto rounded-xl bg-slate-900 p-4 text-xs leading-6 text-slate-100">
          {source.sql}
        </pre>
        <pre className="overflow-x-auto rounded-xl border border-[var(--border)] bg-white p-4 text-xs leading-6 text-slate-700">
          {source.results}
        </pre>
      </div>
    </details>
  );
}

export default function SourceList({ sources }: { sources: Source[] }) {
  if (!sources.length) return null;

  return (
    <div className="mt-5 space-y-3">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--muted)]">
        Citations
      </p>
      {sources.map((source, index) =>
        source.type === "sql" ? (
          <SqlSource key={`sql-${index}`} source={source} />
        ) : (
          <DocumentSource
            key={`${source.source_document}-${index}`}
            source={source}
            index={index}
          />
        )
      )}
    </div>
  );
}
