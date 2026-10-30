import { type ReactNode, createContext, useCallback, useContext, useMemo, useState } from "react";

/**
 * Stand-in identity until agency sign-in exists: the user picks a demo user, and the API client sends it in the
 * `X-Demo-User` header. When real sign-in lands, this provider is the one place that changes.
 */
export const DEMO_USERS = [
  { id: "indiana.analyst", label: "Indiana analyst" },
  { id: "iowa.analyst", label: "Iowa analyst" },
  { id: "ohio.analyst", label: "Ohio analyst" },
  { id: "support.staff", label: "Customer support (internal)" },
] as const;

const STORAGE_KEY = "agency-reports.demo-user";
const DEFAULT_USER = "support.staff";

type IdentityValue = {
  userId: string;
  setUserId: (userId: string) => void;
};

const IdentityContext = createContext<IdentityValue | null>(null);

let currentUserId = readStoredUser();

/** The API client reads this; components use `useIdentity` instead. */
export function getCurrentUserId(): string {
  return currentUserId;
}

export function IdentityProvider({ children }: { children: ReactNode }) {
  const [userId, setUserIdState] = useState(currentUserId);

  const setUserId = useCallback((next: string) => {
    currentUserId = next;
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // Storage can be unavailable (private mode); the choice then lasts for this page load only.
    }
    setUserIdState(next);
  }, []);

  const value = useMemo(() => ({ userId, setUserId }), [userId, setUserId]);
  return <IdentityContext.Provider value={value}>{children}</IdentityContext.Provider>;
}

export function useIdentity(): IdentityValue {
  const value = useContext(IdentityContext);
  if (!value) throw new Error("useIdentity must be used inside <IdentityProvider>");
  return value;
}

function readStoredUser(): string {
  try {
    return localStorage.getItem(STORAGE_KEY) ?? DEFAULT_USER;
  } catch {
    return DEFAULT_USER;
  }
}
