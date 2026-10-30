import type { ReactNode } from "react";
import { NavLink } from "react-router";
import { DEMO_USERS, useIdentity } from "../lib/identity.js";
import { NAV_ITEMS } from "../nav.js";

export function AppShell({ children }: { children: ReactNode }) {
  const { userId, setUserId } = useIdentity();

  return (
    <div className="shell">
      <header className="shell__header">
        <span className="shell__title">Agency Reports</span>
        <label className="shell__user">
          <span>Viewing as</span>
          <select value={userId} onChange={(event) => setUserId(event.target.value)}>
            {DEMO_USERS.map((user) => (
              <option key={user.id} value={user.id}>
                {user.label}
              </option>
            ))}
          </select>
        </label>
      </header>
      <nav className="shell__nav" aria-label="Reports">
        {NAV_ITEMS.map((item) => (
          <NavLink key={item.path} to={item.path}>
            {item.label}
          </NavLink>
        ))}
      </nav>
      <main className="shell__main">{children}</main>
    </div>
  );
}
