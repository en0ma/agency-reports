import { Navigate, Route, Routes } from "react-router";
import { AppShell } from "./components/AppShell.js";
import { NAV_ITEMS } from "./nav.js";

export function App() {
  return (
    <AppShell>
      <Routes>
        {NAV_ITEMS.map(({ path, element }) => (
          <Route key={path} path={path} element={element} />
        ))}
        <Route path="*" element={<Navigate to={NAV_ITEMS[0]?.path ?? "/"} replace />} />
      </Routes>
    </AppShell>
  );
}
