import type { ReactElement } from "react";
import { CmvAlertsPage } from "./pages/CmvAlertsPage.js";

export type NavItem = {
  path: string;
  label: string;
  element: ReactElement;
};

/** Report pages in the side navigation. Adding a report = adding an entry here. */
export const NAV_ITEMS: readonly NavItem[] = [
  { path: "/cmv-alerts", label: "CMV Traffic Alerts", element: <CmvAlertsPage /> },
];
