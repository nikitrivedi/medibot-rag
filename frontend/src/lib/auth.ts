import type { Session } from "./types";

const SESSION_KEY = "medibot_session";

const DEPARTMENT_ACCESS: Record<string, string[]> = {
  billing: ["billing_executive", "admin"],
  clinical: ["doctor", "admin"],
  nursing: ["nurse", "doctor", "admin"],
  equipment: ["technician", "admin"],
  general: ["billing_executive", "doctor", "nurse", "admin", "technician"],
};

const SQL_RAG_ROLES = new Set(["billing_executive", "admin"]);

const ROLE_LABELS: Record<string, string> = {
  billing_executive: "Billing Executive",
  doctor: "Doctor",
  nurse: "Nurse",
  technician: "Technician",
  admin: "Admin",
};

export function getRoleLabel(role: string): string {
  return ROLE_LABELS[role] ?? role;
}

export function getAccessibleCollections(role: string): string[] {
  return Object.entries(DEPARTMENT_ACCESS)
    .filter(([, roles]) => roles.includes(role))
    .map(([collection]) => collection);
}

export function hasSqlAccess(role: string): boolean {
  return SQL_RAG_ROLES.has(role);
}

export function saveSession(session: Session): void {
  try {
    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
  } catch {
    throw new Error("Could not save session. Check that browser storage is enabled.");
  }
}

export function loadSession(): Session | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(SESSION_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as Session;
  } catch {
    return null;
  }
}

export function clearSession(): void {
  localStorage.removeItem(SESSION_KEY);
}

export const DEMO_USERS = [
  { username: "billing", password: "billing123", hint: "Billing + SQL analytics" },
  { username: "doctor", password: "doctor123", hint: "Clinical + nursing docs" },
  { username: "nurse", password: "nurse123", hint: "Nursing procedures" },
  { username: "tech", password: "tech123", hint: "Equipment manuals" },
  { username: "admin", password: "admin123", hint: "Full access + SQL" },
];
