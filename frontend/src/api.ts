/** Single origin only. If someone pastes a CORS-style list by mistake, prefer https. */
function normalizeApiBase(raw: string): string {
  const trimmed = raw.trim().replace(/\/$/, "");
  if (!trimmed.includes(",")) return trimmed;
  const parts = trimmed
    .split(",")
    .map((p) => p.trim().replace(/\/$/, ""))
    .filter(Boolean);
  const https = parts.find((p) => p.startsWith("https://"));
  if (https) return https;
  return parts[parts.length - 1] ?? trimmed;
}

const base = (): string => {
  const env = import.meta.env.VITE_API_URL;
  if (env && env.length > 0) return normalizeApiBase(env);
  if (import.meta.env.DEV) return "/api";
  return "";
};

const DEFAULT_TIMEOUT_MS = 30_000;
const INGEST_TIMEOUT_MS = 180_000;

function signalForTimeout(ms: number): AbortSignal {
  if (typeof AbortSignal !== "undefined" && typeof AbortSignal.timeout === "function") {
    return AbortSignal.timeout(ms);
  }
  const c = new AbortController();
  setTimeout(() => c.abort(), ms);
  return c.signal;
}

async function getJson<T>(path: string, timeoutMs = DEFAULT_TIMEOUT_MS): Promise<T> {
  const b = base();
  if (!b && !import.meta.env.DEV) {
    throw new Error(
      "API base URL is not configured (set VITE_API_URL when building the frontend)."
    );
  }
  const r = await fetch(`${b}${path}`, { signal: signalForTimeout(timeoutMs) });
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json() as Promise<T>;
}

export type Source = {
  id: string;
  name: string;
  kind: string;
  feed_url: string | null;
  scraper_module: string | null;
  enabled: boolean;
};

export type Item = {
  id: number;
  source_id: string;
  title: string;
  url: string;
  summary: string | null;
  published_at: string | null;
  fetched_at: string;
};

export type Weather = {
  latitude: number;
  longitude: number;
  timezone: string;
  current: {
    temperature_c: number;
    windspeed_kmh: number;
    weathercode: number;
    is_day: number;
  };
};

export type Status = {
  source_count: number;
  item_count: number;
  last_fetched_at: string | null;
};

export type IngestResult = {
  sources_processed: number;
  items_upserted: number;
  errors: string[];
};

export function fetchSources() {
  return getJson<Source[]>("/sources");
}

export function fetchItems(params: { sourceId?: string; limit?: number }) {
  const q = new URLSearchParams();
  if (params.sourceId) q.set("source_id", params.sourceId);
  if (params.limit) q.set("limit", String(params.limit));
  const qs = q.toString();
  return getJson<Item[]>(`/items${qs ? `?${qs}` : ""}`);
}

export function fetchWeather() {
  return getJson<Weather>("/weather");
}

export function fetchStatus() {
  return getJson<Status>("/status");
}

export async function runIngest(): Promise<IngestResult> {
  const b = base();
  if (!b && !import.meta.env.DEV) {
    throw new Error(
      "API base URL is not configured (set VITE_API_URL when building the frontend)."
    );
  }
  const r = await fetch(`${b}/ingest/run`, {
    method: "POST",
    signal: signalForTimeout(INGEST_TIMEOUT_MS),
  });
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json() as Promise<IngestResult>;
}

/** Short WMO-ish label for Open-Meteo weather codes (simplified). */
export function weatherLabel(code: number): string {
  if (code === 0) return "Clear";
  if (code <= 3) return "Partly cloudy";
  if (code <= 48) return "Fog";
  if (code <= 57) return "Drizzle";
  if (code <= 67) return "Rain";
  if (code <= 77) return "Snow";
  if (code <= 82) return "Rain showers";
  if (code <= 86) return "Snow showers";
  if (code <= 99) return "Storm";
  return "Weather";
}
