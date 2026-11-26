import { beforeEach, describe, expect, it } from "vitest";
import { readStoredValue, writeStoredValue } from "./storage";

const values = new Map<string, string>();
beforeEach(() => {
  values.clear();
  Object.defineProperty(globalThis, "localStorage", {
    configurable: true,
    value: {
      getItem: (key: string) => values.get(key) ?? null,
      setItem: (key: string, value: string) => values.set(key, value),
      removeItem: (key: string) => values.delete(key),
      clear: () => values.clear(),
    },
  });
});

describe("typed local cache", () => {
  it("persists typed values", () => {
    writeStoredValue("activeView", "support");
    expect(readStoredValue("activeView", "garage")).toBe("support");
  });

  it("uses a fallback for malformed values", () => {
    values.set("manutencar:activeView", "{bad");
    expect(readStoredValue("activeView", "garage")).toBe("garage");
  });
});
