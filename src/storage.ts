export function readStoredValue<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(`manutencar:${key}`);
    return raw ? JSON.parse(raw) as T : fallback;
  } catch {
    return fallback;
  }
}

export function writeStoredValue<T>(key: string, value: T): void {
  localStorage.setItem(`manutencar:${key}`, JSON.stringify(value));
}
