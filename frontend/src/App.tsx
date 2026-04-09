import { lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  fetchAlerts,
  fetchItems,
  fetchSources,
  fetchStatus,
  fetchWeather,
  runEnrichment,
  runIngest,
  weatherLabel,
  type AlertsResponse,
  type Item,
  type Source,
  type Status,
  type Weather,
} from "./api";

const MapView = lazy(() => import("./MapView"));

function formatWhen(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function categoryLabel(c: string): string {
  if (c === "safety") return "Safety";
  if (c === "infrastructure") return "Infrastructure";
  if (c === "event") return "Event";
  return "News";
}

export default function App() {
  const [sources, setSources] = useState<Source[]>([]);
  const [items, setItems] = useState<Item[]>([]);
  const [weather, setWeather] = useState<Weather | null>(null);
  const [status, setStatus] = useState<Status | null>(null);
  const [alerts, setAlerts] = useState<AlertsResponse>({ high_alert: false, breaking: [] });
  const [filterSource, setFilterSource] = useState<string>("");
  const [filterCategory, setFilterCategory] = useState<string>("");
  const [view, setView] = useState<"list" | "map">("list");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [ingestBusy, setIngestBusy] = useState(false);
  const [enrichBusy, setEnrichBusy] = useState(false);
  const [ingestMsg, setIngestMsg] = useState<string | null>(null);
  const listRef = useRef<HTMLUListElement | null>(null);

  const sourceById = useMemo(() => {
    const m = new Map<string, Source>();
    for (const s of sources) m.set(s.id, s);
    return m;
  }, [sources]);

  const load = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      const [src, it, wx, st, al] = await Promise.all([
        fetchSources(),
        fetchItems({
          sourceId: filterSource || undefined,
          category: filterCategory || undefined,
          limit: 300,
        }),
        fetchWeather().catch(() => null),
        fetchStatus(),
        fetchAlerts(48).catch(() => ({ high_alert: false, breaking: [] })),
      ]);
      setSources(src);
      setItems(it);
      setWeather(wx);
      setStatus(st);
      setAlerts(al);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  }, [filterSource, filterCategory]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (selectedId == null || !listRef.current) return;
    const el = listRef.current.querySelector(`[data-item-id="${selectedId}"]`);
    el?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [selectedId, view, items]);

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

  const onEnrich = async () => {
    setEnrichBusy(true);
    setIngestMsg(null);
    try {
      const r = await runEnrichment();
      setIngestMsg(
        r.llm_configured
          ? `Enrichment finished (${r.processed} item(s) updated).`
          : "No LLM configured (set OLLAMA_BASE_URL or GROQ_API_KEY on the API)."
      );
      await load();
    } catch (e) {
      setIngestMsg(e instanceof Error ? e.message : "Enrichment failed");
    } finally {
      setEnrichBusy(false);
    }
  };

  return (
    <div className={`layout${alerts.high_alert ? " high-alert" : ""}`}>
      <header className="header">
        <div className="header-inner">
          <h1 className="title">Puerto Vallarta Intelligence</h1>
          <p className="subtitle">
            Banderas Bay monitor: news, safety signals, and map layers — RSS + optional LLM enrichment.
          </p>
        </div>
      </header>

      {alerts.breaking.length > 0 && (
        <div className="ticker-wrap" role="region" aria-label="Breaking signals">
          <span className="ticker-label">{alerts.high_alert ? "High alert" : "Monitor"}</span>
          <div className="ticker">
            <div className="ticker-track">
              {[...alerts.breaking, ...alerts.breaking].map((b, i) => (
                <a
                  key={`${b.id}-${i}`}
                  href={b.url}
                  target="_blank"
                  rel="noreferrer noopener"
                  className="ticker-item"
                >
                  {b.title}
                </a>
              ))}
            </div>
          </div>
        </div>
      )}

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

        <section className="toolbar toolbar-wrap">
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
          <label className="field">
            <span className="label">Category</span>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="select"
            >
              <option value="">All</option>
              <option value="general">General</option>
              <option value="safety">Safety</option>
              <option value="infrastructure">Infrastructure</option>
              <option value="event">Events</option>
            </select>
          </label>
          <div className="view-tabs">
            <button
              type="button"
              className={`tab ${view === "list" ? "active" : ""}`}
              onClick={() => setView("list")}
            >
              List
            </button>
            <button
              type="button"
              className={`tab ${view === "map" ? "active" : ""}`}
              onClick={() => setView("map")}
            >
              Map
            </button>
          </div>
          <button type="button" className="btn secondary" onClick={() => void load()} disabled={loading}>
            Refresh
          </button>
          <button type="button" className="btn primary" onClick={() => void onIngest()} disabled={ingestBusy}>
            {ingestBusy ? "Ingesting…" : "Run ingest"}
          </button>
          <button type="button" className="btn secondary" onClick={() => void onEnrich()} disabled={enrichBusy}>
            {enrichBusy ? "Enriching…" : "Run LLM enrich"}
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
              <h2 className="panel-title">{view === "map" ? "Map" : "Headlines"}</h2>
              {status && (
                <span className="muted small">
                  {status.item_count} items · {status.source_count} sources
                </span>
              )}
            </div>
            {view === "map" ? (
              <Suspense fallback={<p className="muted">Loading map…</p>}>
                <MapView items={items} selectedId={selectedId} onSelect={setSelectedId} />
              </Suspense>
            ) : loading ? (
              <p className="muted">Loading…</p>
            ) : items.length === 0 ? (
              <p className="muted">No items yet. Run ingest or check your feeds in config.</p>
            ) : (
              <ul className="item-list" ref={listRef}>
                {items.map((it) => {
                  const src = sourceById.get(it.source_id);
                  return (
                    <li
                      key={it.id}
                      className={`item-row${selectedId === it.id ? " selected" : ""}`}
                      data-item-id={it.id}
                    >
                      <div className="item-top">
                        <span className="badge">{src?.name ?? it.source_id}</span>
                        <span className={`cat cat-${it.category}`}>{categoryLabel(it.category)}</span>
                        {it.severity !== "normal" && (
                          <span className={`sev sev-${it.severity}`}>{it.severity}</span>
                        )}
                        <time className="muted small" dateTime={it.published_at ?? undefined}>
                          {formatWhen(it.published_at)}
                        </time>
                      </div>
                      <button
                        type="button"
                        className="item-title-btn"
                        onClick={() => setSelectedId(it.id === selectedId ? null : it.id)}
                      >
                        {it.title}
                      </button>
                      <a
                        href={it.url}
                        target="_blank"
                        rel="noreferrer noopener"
                        className="item-open small"
                      >
                        Open article
                      </a>
                      {(it.summary_en || it.summary_es || it.summary) && (
                        <p className="item-summary muted">
                          {stripHtml(it.summary_en || it.summary_es || it.summary || "")}
                        </p>
                      )}
                      {it.neighborhood && (
                        <p className="muted small">Area: {it.neighborhood}</p>
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
          Map markers use keyword geocoding + LLM hints. Not a substitute for official emergency channels.
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
