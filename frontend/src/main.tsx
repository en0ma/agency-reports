import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";
import { App } from "./App.js";
import { IdentityProvider } from "./lib/identity.js";
import "./styles.css";

const root = document.getElementById("root");
if (!root) throw new Error("Missing #root element");

createRoot(root).render(
  <StrictMode>
    <BrowserRouter>
      <IdentityProvider>
        <App />
      </IdentityProvider>
    </BrowserRouter>
  </StrictMode>,
);
