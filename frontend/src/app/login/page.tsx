"use client";

import { FormEvent, useEffect, useState } from "react";
import { login } from "@/lib/api";
import { DEMO_USERS, loadSession, saveSession } from "@/lib/auth";

export default function LoginPage() {
  const [username, setUsername] = useState("billing");
  const [password, setPassword] = useState("billing123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (loadSession()) {
      window.location.href = "/chat";
    }
  }, []);

  async function signIn(user: string, pass: string) {
    setError("");
    setLoading(true);

    try {
      const session = await login(user, pass);
      saveSession(session);
      window.location.href = "/chat";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
      setLoading(false);
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    signIn(username, password);
  }

  return (
    <main className="min-h-screen lg:grid lg:grid-cols-[1.05fr_0.95fr]">
      <section className="relative hidden overflow-hidden px-12 py-16 lg:flex lg:flex-col lg:justify-center">
        <div className="absolute inset-0 bg-gradient-to-br from-[#0d6e63] via-[#0f5f78] to-[#1d4ed8] opacity-95" />
        <div className="absolute -left-16 top-20 h-56 w-56 rounded-full bg-white/10 blur-3xl" />
        <div className="absolute bottom-0 right-0 h-72 w-72 rounded-full bg-cyan-200/20 blur-3xl" />

        <div className="relative z-10 max-w-lg">
          <h1 className="text-5xl font-semibold leading-tight text-white">
            Medical Bot Assistant
          </h1>
          <p className="mt-5 text-lg leading-8 text-white/80">
            Query clinical, nursing, billing, and equipment knowledge.
          </p>
        </div>
      </section>

      <section className="flex items-center justify-center px-6 py-10 lg:px-12">
        <div className="glass-card w-full max-w-md rounded-3xl p-8">
          <div className="mb-8 lg:hidden">
            <h1 className="text-3xl font-semibold">Medical Bot Assistant</h1>
            <p className="mt-2 text-sm leading-6 text-[var(--muted)]">
              Query clinical, nursing, billing, and equipment knowledge.
            </p>
          </div>

          <div className="mb-8 hidden lg:block">
            <h2 className="text-2xl font-semibold">Sign in</h2>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Username
              </label>
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-muted)] px-4 py-3 transition focus:bg-white"
                required
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-muted)] px-4 py-3 transition focus:bg-white"
                required
              />
            </div>
            {error && (
              <div className="rounded-xl border border-red-100 bg-[var(--danger-soft)] px-4 py-3 text-sm text-[var(--danger)]">
                {error}
              </div>
            )}
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-[var(--primary)] px-4 py-3 font-medium text-white transition hover:bg-[var(--primary-hover)] disabled:opacity-60"
            >
              {loading ? "Signing in..." : "Continue to assistant"}
            </button>
          </form>

          <div className="mt-8">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--muted)]">
              Demo accounts
            </p>
            <div className="mt-3 space-y-2">
              {DEMO_USERS.map((user) => (
                <button
                  key={user.username}
                  type="button"
                  disabled={loading}
                  onClick={() => signIn(user.username, user.password)}
                  className="flex w-full items-center justify-between rounded-xl border border-[var(--border)] bg-[var(--surface-muted)] px-4 py-3 text-left transition hover:border-[var(--primary)] hover:bg-white disabled:opacity-60"
                >
                  <span className="font-medium capitalize">{user.username}</span>
                  <span className="text-sm text-[var(--muted)]">{user.hint}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
