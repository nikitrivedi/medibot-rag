import { getAccessibleCollections, getRoleLabel, hasSqlAccess } from "@/lib/auth";
import type { Session } from "@/lib/types";

type SidebarProps = {
  session: Session;
  onLogout: () => void;
};

const COLLECTION_LABELS: Record<string, string> = {
  billing: "Billing",
  clinical: "Clinical",
  nursing: "Nursing",
  equipment: "Equipment",
  general: "General",
};

const COLLECTION_COLORS: Record<string, string> = {
  billing: "bg-amber-50 text-amber-800 border-amber-100",
  clinical: "bg-rose-50 text-rose-800 border-rose-100",
  nursing: "bg-sky-50 text-sky-800 border-sky-100",
  equipment: "bg-violet-50 text-violet-800 border-violet-100",
  general: "bg-slate-50 text-slate-700 border-slate-200",
};

export default function Sidebar({ session, onLogout }: SidebarProps) {
  const collections = getAccessibleCollections(session.role);

  return (
    <aside className="flex h-screen w-80 shrink-0 flex-col border-r border-[var(--border)] bg-[var(--surface)]">
      <div className="border-b border-[var(--border)] px-6 py-6">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[var(--primary-soft)] text-lg font-semibold text-[var(--primary)]">
            M
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--muted)]">
              MediAssist
            </p>
            <h1 className="text-lg font-semibold">MediBot RAG</h1>
          </div>
        </div>
      </div>

      <div className="flex-1 space-y-6 overflow-y-auto px-6 py-6">
        <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-muted)] p-4">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--muted)]">
            Signed in as
          </p>
          <p className="mt-2 text-base font-semibold">@{session.username}</p>
          <span className="mt-3 inline-flex rounded-full bg-[var(--primary-soft)] px-3 py-1 text-sm font-medium text-[var(--primary)]">
            {getRoleLabel(session.role)}
          </span>
        </div>

        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--muted)]">
            Accessible collections
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {collections.map((collection) => (
              <span
                key={collection}
                className={`rounded-full border px-3 py-1 text-xs font-medium ${
                  COLLECTION_COLORS[collection] ?? "bg-slate-50 text-slate-700 border-slate-200"
                }`}
              >
                {COLLECTION_LABELS[collection] ?? collection}
              </span>
            ))}
          </div>
        </div>

        {hasSqlAccess(session.role) ? (
          <div className="rounded-2xl border border-[var(--accent-soft)] bg-[var(--accent-soft)] p-4">
            <p className="text-sm font-medium text-[var(--accent)]">SQL analytics enabled</p>
            <p className="mt-1 text-sm leading-6 text-slate-600">
              Count, total, and trend questions route to the hospital database.
            </p>
          </div>
        ) : (
          <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-muted)] p-4 text-sm leading-6 text-[var(--muted)]">
            Document answers are limited to the collections available for your role.
          </div>
        )}
      </div>

      <div className="border-t border-[var(--border)] p-6">
        <button
          onClick={onLogout}
          className="w-full rounded-xl border border-[var(--border)] bg-white px-4 py-3 text-sm font-medium text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
        >
          Log out
        </button>
      </div>
    </aside>
  );
}
