const base = (): string => {
  const env = import.meta.env.VITE_API_URL;
  if (env && env.length > 0) return env.replace(/\/$/, "");
  if (import.meta.env.DEV) return "/api";
  return "";
};

async function getJson<T>(path: string): Promise<T> {
  const r = await fetch(`${base()}${path}`);
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
  const r = await fetch(`${base()}/ingest/run`, { method: "POST" });
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
