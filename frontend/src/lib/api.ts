import type { ChatResponse, LoginResponse, Session } from "./types";

// Empty base uses the Next.js proxy in next.config.ts (same-origin /api/*).
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

function apiUrl(path: string): string {
  return `${API_BASE}${path}`;
}

export async function login(
  username: string,
  password: string
): Promise<LoginResponse> {
  let res: Response;
  try {
    res = await fetch(apiUrl("/api/login"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
  } catch {
    throw new Error(
      "Cannot reach the API server. Start the backend with: uv run uvicorn index:app --reload --port 8000"
    );
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = err.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((item: { msg?: string }) => item.msg).join(", ")
          : "Login failed";
    throw new Error(message || "Login failed");
  }

  return res.json();
}

export async function chat(
  question: string,
  session: Session
): Promise<ChatResponse> {
  let res: Response;
  try {
    res = await fetch(apiUrl("/api/chat"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.access_token}`,
      },
      body: JSON.stringify({ question, role: session.role }),
    });
  } catch {
    throw new Error("Cannot reach the API server.");
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? "Chat request failed");
  }

  return res.json();
}
