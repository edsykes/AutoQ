import { render, screen, waitFor } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { App } from "./App";

it("shows API health", async () => {
  vi.stubGlobal("fetch", async () => ({ json: async () => ({ status: "ok", database: "ok" }) }));
  render(<App />);
  await waitFor(() => expect(screen.getByTestId("api-health").textContent).toContain("ok"));
});
