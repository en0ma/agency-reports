import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";
import { clearApiDataCache } from "../src/lib/use-api-data.js";

afterEach(() => {
  cleanup();
  clearApiDataCache();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});
