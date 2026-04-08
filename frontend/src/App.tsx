import { useCallback, useEffect, useMemo, useState } from "react";
import {
  fetchItems,
  fetchSources,
  fetchStatus,
  fetchWeather,
  runIngest,
  weatherLabel,
  type Item,
  type Source,
  type Status,
  type Weather,
} from "./api";

function formatWhen(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function App() {
  const [sources, setSources] = useState<Source[]>([]);
  const [items, setItems] = useState<Item[]>([]);
  const [weather, setWeather] = useState<Weather | null>(null);
  const [status, setStatus] = useState<Status | null>(null);
  const [filterSource, setFilterSource] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [ingestBusy, setIngestBusy] = useState(false);
  const [ingestMsg, setIngestMsg] = useState<string | null>(null);

  const sourceById = useMemo(() => {
    const m = new Map<string, Source>();
    for (const s of sources) m.set(s.id, s);
    return m;
  }, [sources]);

  const load = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      const [src, it, wx, st] = await Promise.all([
        fetchSources(),
        fetchItems({ sourceId: filterSource || undefined, limit: 200 }),
        fetchWeather().catch(() => null),
        fetchStatus(),
      ]);
      setSources(src);
      setItems(it);
      setWeather(wx);
      setStatus(st);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  }, [filterSource]);

  useEffect(() => {
    void load();
  }, [load]);

  const onIngest = async () => {
    setIngestBusy(true);
    setIngestMsg(null);
    try {
      const r = await runIngest();
      setIngestMsg(
        r.errors.length
          ? `Ingest done with ${r.errors.length} error(s).`
          : `Ingest ok: +${r.items_upserted} new items.`
      );
      await load();
    } catch (e) {
      setIngestMsg(e instanceof Error ? e.message : "Ingest failed");
    } finally {
      setIngestBusy(false);
    }
  };

  return (
    <div className="layout">
      <header className="header">
        <div className="header-inner">
          <h1 className="title">Puerto Vallarta Intelligence</h1>
          <p className="subtitle">
            Latest headlines from configured RSS feeds and scrapers, plus local
            weather.
          </p>
        </div>
      </header>

      <main className="main">
        {error && (
          <div className="banner error" role="alert">
            {error}
          </div>
        )}
        {ingestMsg && (
          <div className="banner info" role="status">
            {ingestMsg}
          </div>
        )}

        <section className="toolbar">
          <label className="field">
            <span className="label">Source</span>
            <select
              value={filterSource}
              onChange={(e) => setFilterSource(e.target.value)}
              className="select"
            >
              <option value="">All sources</option>
              {sources.map((s) => (
                <option key={s.id} value={s.id} disabled={!s.enabled}>
                  {s.name}
                  {!s.enabled ? " (disabled)" : ""}
                </option>
              ))}
            </select>
          </label>
          <button type="button" className="btn secondary" onClick={() => void load()} disabled={loading}>
            Refresh
          </button>
          <button type="button" className="btn primary" onClick={() => void onIngest()} disabled={ingestBusy}>
            {ingestBusy ? "Ingesting…" : "Run ingest now"}
          </button>
        </section>

        <div className="grid">
          <section className="panel weather-panel">
            <h2 className="panel-title">Weather · Puerto Vallarta</h2>
            {loading && !weather ? (
              <p className="muted">Loading…</p>
            ) : weather ? (
              <div className="weather-body">
                <div className="weather-temp">{Math.round(weather.current.temperature_c)}°C</div>
                <div className="weather-meta">
                  <div>{weatherLabel(weather.current.weathercode)}</div>
                  <div>Wind {Math.round(weather.current.windspeed_kmh)} km/h</div>
                  <div className="muted small">
                    Open-Meteo · {weather.timezone}
                  </div>
                </div>
              </div>
            ) : (
              <p className="muted">Weather unavailable (check API or network).</p>
            )}
          </section>

          <section className="panel list-panel">
            <div className="panel-head">
              <h2 className="panel-title">Headlines</h2>
              {status && (
                <span className="muted small">
                  {status.item_count} items · {status.source_count} sources
                </span>
              )}
            </div>
            {loading ? (
              <p className="muted">Loading…</p>
            ) : items.length === 0 ? (
              <p className="muted">No items yet. Run ingest or check your feeds in config.</p>
            ) : (
              <ul className="item-list">
                {items.map((it) => {
                  const src = sourceById.get(it.source_id);
                  return (
                    <li key={it.id} className="item-row">
                      <div className="item-top">
                        <span className="badge">{src?.name ?? it.source_id}</span>
                        <time className="muted small" dateTime={it.published_at ?? undefined}>
                          {formatWhen(it.published_at)}
                        </time>
                      </div>
                      <a href={it.url} target="_blank" rel="noreferrer noopener" className="item-title">
                        {it.title}
                      </a>
                      {it.summary && (
                        <p className="item-summary muted">{stripHtml(it.summary)}</p>
                      )}
                    </li>
                  );
                })}
              </ul>
            )}
          </section>
        </div>
      </main>

      <footer className="footer">
        <span>
          Last ingest / fetch:{" "}
          <strong>{formatWhen(status?.last_fetched_at ?? null)}</strong>
        </span>
        <span className="muted small">
          Data from your configured sources; links open the original publisher.
        </span>
      </footer>
    </div>
  );
}

function stripHtml(html: string): string {
  const doc = new DOMParser().parseFromString(html, "text/html");
  const t = doc.body.textContent?.trim() ?? html;
  return t.length > 280 ? `${t.slice(0, 277)}…` : t;
}
